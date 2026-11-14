"""내보내기 판 8 인계 세트(`fixtures/picasso-0.11.0-export-8/`) — 운영 경로가 판 8 번들을 받고, 새 칸마다 읽는 자리가 있는가.

picasso 인계 `audit-export-8.md`(§15.322)의 「지을 읽는 코드」를 실물 번들로 본다. 재기동 장면(`run-5a` → `run-5b`)이 같은
`incidentKey` 로 이어지는데 재발로 세지 않는 것이 핵심이다.
"""

import json
import pathlib

import pytest

from composer.query import compose, compose_search
from receiver.approval import candidates
from receiver.export import read_export
from receiver.history import count_recurrence, subject
from receiver.run import once
from receiver.scan import scan
from recorder.store import RecordStore

SET = pathlib.Path(__file__).parent / "fixtures" / "picasso-0.11.0-export-8"
V7 = pathlib.Path(__file__).parent / "fixtures" / "picasso-0.11.0"
RUNS = ("run-1", "run-2", "run-3", "run-4", "run-5a", "run-5b")


def _ok(query, search_text=None):
    return 200, {"success": True, "data": {"llm_failed": False, "answer": "…", "citations": [{"verified": True}]}}


@pytest.mark.parametrize("run", RUNS)
def test_판_8_세트의_줄마다_설명이_한_건씩_붙는다(tmp_path, run):
    """여섯 벌 다 빠지는 줄 없이 한 건씩 적힌다. 판단자는 종류만 질의에 실리고 원문 id 는 감사 항목에만 남는다."""
    folder = SET / run
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert (manifest["schemaVersion"], manifest["contractSemver"]) == ("8", "0.11.0") and manifest["instanceId"]
    store = RecordStore(tmp_path / "explanations.jsonl")
    asked = []

    written = once(folder, store, search=lambda q, search_text=None: (asked.append(q), _ok(q))[1])

    counts = manifest["counts"]
    assert written == len(store.load()) == counts["incidents"] + counts["remedySearches"]
    batch = scan(folder, set())
    records = {r.key[1]: r for r in store.load()}
    for bundle in batch.incidents:
        fact = compose(bundle).facts
        assert fact["openingKind"] == bundle["openingKind"]
        step = bundle["resolution"]
        audit = records[bundle["digest"]].audit
        if step is None:
            assert "resolution" not in fact and audit == {}
            continue
        assert fact["resolution"] == {"decision": step["decision"], "at": step["at"],
                                      "decidedByKind": step["decidedBy"]["kind"]}
        assert audit["decidedBy"] == step["decidedBy"] and audit["incidentKey"] == bundle["incidentKey"]
        assert audit["sameIdAsApprover"] is (None if bundle["approvedBy"] is None
                                             else bundle["approvedBy"]["id"] == step["decidedBy"]["id"])
        # 원문 id 는 설명 생성 입력에 안 간다 — 질의 글에도 검색 텍스트에도 없다
        assert step["decidedBy"]["id"] not in compose(bundle).text + compose(bundle).search_text
    assert not any(b["resolution"]["decidedBy"]["id"] in q for q in asked
                   for b in batch.incidents if b["resolution"])


def test_판_8_의_요약은_판_7_과_같다():
    """새 칸은 해시에서 빠져 같은 시드의 `digest` 가 그대로다 — 멱등성 키 `(runId, digest)` 도 그대로 쓴다."""
    for run in ("run-1", "run-2", "run-3", "run-4"):
        assert ([b["digest"] for b in read_export(SET / run).incidents]
                == [b["digest"] for b in read_export(V7 / run).incidents]), run


def test_재기동_장면은_같은_열쇠로_이어지고_재발이_아니다(tmp_path):
    """`run-5a`(앞 인스턴스, `NEW`) 뒤에 `run-5b`(다시 지은 인스턴스, 같은 보류를 다시 연 `REOPENED`)를 받는다. 두 줄은 같은
    `incidentKey` · `firstOpenedAt` 이고 `digest` · `instanceId` · `at` 이 다르다. 저장소를 거쳐도(지난 번들의 주체) 다시 연
    인시던트에게 원래 보류는 앞선 사건이 아니다."""
    first, second = read_export(SET / "run-5a"), read_export(SET / "run-5b")
    a, b = first.incidents[0], second.incidents[0]
    assert (a["openingKind"], b["openingKind"]) == ("NEW", "REOPENED")
    assert a["incidentKey"] == b["incidentKey"] and a["firstOpenedAt"] == b["firstOpenedAt"]
    assert a["digest"] != b["digest"] and a["at"] != b["at"]
    assert first.manifest["instanceId"] != second.manifest["instanceId"]

    store = RecordStore(tmp_path / "explanations.jsonl")
    once(SET / "run-5a", store, search=_ok)
    prior = store.subjects()
    assert prior[0]["incidentKey"] == a["incidentKey"]

    assert count_recurrence(b, prior + [subject(b)]) == {"sameRobotSameClass": 0, "sameUnitSameClass": 0}
    assert compose(b, recurrence=count_recurrence(b, prior)).facts["recurrenceSeen"] == {
        "sameRobotSameClass": 0, "sameUnitSameClass": 0}

    # 판 7 까지의 읽는 법(열쇠 없이 근거 창의 시각 추정)이면 원래 보류를 한 번 센다 — 판 8 이 고친 자리다
    def as_v7(row):
        return {k: v for k, v in row.items() if k not in ("incidentKey", "firstOpenedAt", "openingKind", "attempt")}
    assert count_recurrence(as_v7(b), [subject(as_v7(a))])["sameRobotSameClass"] == 1

    # 두 줄은 한 사건이다 — 뒤에 같은 자리에서 새로 선 사건에게는 한 번만 앞선다
    later = dict(a, incidentKey="mw-later/incident-1", firstOpenedAt="2026-09-06T00:00:30Z", at="2026-09-06T00:00:30Z",
                 digest="later")
    assert count_recurrence(later, [subject(a), subject(b)]) == {"sameRobotSameClass": 1, "sameUnitSameClass": 1}


def test_임무_버전과_현장_설정_셋은_봉인_라운드의_값으로_실린다():
    """`run-5a`·`run-5b` 만 임무 정의와 현장 설정으로 돌아 값이 있다. 의도에서 꺼내 따로 싣고, 넷 다 널인 `run-1`~`run-4` 는
    안 싣는다 — 널은 「모름」이 아니라 코드 정의 · 설정 없이 돈 실행이라 「모름」으로 적지 않는다."""
    facts = compose(read_export(SET / "run-5b").incidents[0]).facts
    assert facts["missionVersion"] == 1
    assert facts["sealedRoundSettings"] == {"siteSettingsVersion": 3, "inDoubtGrace": "PT20S", "stallWindow": "PT40S"}
    assert not {"missionVersion", "siteSettingsVersion", "inDoubtGrace", "stallWindow"} & set(facts["intent"])
    for run in ("run-1", "run-2", "run-3", "run-4"):
        for bundle in read_export(SET / run).incidents:
            query = compose(bundle)
            assert "missionVersion" not in query.facts and "sealedRoundSettings" not in query.facts, run
            assert "missionVersion" not in query.text and "stallWindow" not in query.text, run


def test_탐색_새_갈래_셋은_사람이_확인하거나_치울_일이고_승인_후보가_아니다():
    """셋 다 `steps` 키가 없고 승인 가능한 조치가 아니다. 질의에는 갈래의 전제와 「사람을 기다린다」를 싣고, 출발 미관측을
    결품(빈 자리)으로 읽지 않으며, 목적지의 신원은 출발 자리의 신원 칸에 섞지 않는다."""
    searches = read_export(SET / "run-5a").searches
    assert [s["outcome"] for s in searches] == ["SOURCE_UNOBSERVED", "DESTINATION_OCCUPIED", "DESTINATION_UNOBSERVED"]
    assert candidates(searches) == []
    unobserved, occupied, silent = (compose_search(s).facts for s in searches)
    assert all(f["remedyAwaitsPerson"] is True for f in (unobserved, occupied, silent))
    assert unobserved["remedySource"] == "SEQ-IN-09.BIN-A" and unobserved["remedyMaterial"] == "ENGINE-COVER-A"
    assert "remedySourceVacant" not in unobserved and "remedySourceOccupied" not in unobserved  # 널은 설비 침묵
    assert occupied == {"robotId": "hum-11", "jobOrderId": "SEQ-FULL-SLOT", "remedyOutcome": "DESTINATION_OCCUPIED",
                        "remedyDestinationObserved": "ENGINE-COVER-B", "remedyDestination": "RACK-208.S01",
                        "remedyAwaitsPerson": True}
    assert silent["remedyDestination"] == "RACK-209.S01" and "remedySteps" not in silent
    # 판 7 까지의 갈래에는 그 표지가 안 붙는다
    assert not any("remedyAwaitsPerson" in compose_search(s).facts for s in read_export(SET / "run-1").searches)
