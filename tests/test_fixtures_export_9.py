"""내보내기 판 9 인계 세트(`fixtures/picasso-0.11.0-export-9/`) — 운영 경로가 판 9 번들을 받고, 재작업 근거를 확인으로 지어내지 않는가.

picasso 인계 `rework-generalized.md`(§15.323)의 「지을 읽는 코드」를 본다. 인계 세트에는 시도된 실패의 재작업이 없어 근거가 전부
널이다 — 값이 있는 근거와 재검사 실패(`REWORK_RECHECK`)는 인계 노트의 모양대로 이 계층이 지은 줄로 본다.
"""

import json
import pathlib

import pytest

from composer.query import compose
from receiver.export import read_export
from receiver.run import once
from receiver.scan import scan
from recorder.store import RecordStore

SET = pathlib.Path(__file__).parent / "fixtures" / "picasso-0.11.0-export-9"
V8 = pathlib.Path(__file__).parent / "fixtures" / "picasso-0.11.0-export-8"
RUNS = ("run-1", "run-2", "run-3", "run-4", "run-5a", "run-5b")
READ_AT = "2026-09-06T00:00:04Z"


def _ok(query, search_text=None):
    return 200, {"success": True, "data": {"llm_failed": False, "answer": "…", "citations": [{"verified": True}]}}


@pytest.mark.parametrize("run", RUNS)
def test_판_9_세트의_줄마다_설명이_한_건씩_붙고_근거_없는_판단은_확인을_싣지_않는다(tmp_path, run):
    """여섯 벌 다 빠지는 줄 없이 한 건씩 적힌다. 판단이 있는 줄마다 `reworkBasis` 키가 있고 이 세트에서는 전부 널이라 질의에
    확인 사실이 안 선다."""
    folder = SET / run
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert (manifest["schemaVersion"], manifest["contractSemver"]) == ("9", "0.11.0") and manifest["instanceId"]
    store = RecordStore(tmp_path / "explanations.jsonl")

    written = once(folder, store, search=_ok)

    counts = manifest["counts"]
    assert written == len(store.load()) == counts["incidents"] + counts["remedySearches"]
    for bundle in scan(folder, set()).incidents:
        step = bundle["resolution"]
        query = compose(bundle)
        if step is None:
            assert "resolution" not in query.facts
            continue
        assert "reworkBasis" in step and step["reworkBasis"] is None
        assert query.facts["resolution"] == {"decision": step["decision"], "at": step["at"],
                                             "decidedByKind": step["decidedBy"]["kind"]}
        assert "reworkChecked" not in query.text


def test_판_9_의_요약과_가상_시각과_탐색_줄은_판_8_과_같다():
    """근거 칸은 판단 칸이라 해시에서 빠진다 — 같은 시드의 `digest` · 가상 시각 · 탐색 줄이 판 8 세트와 같다."""
    for run in RUNS:
        nine, eight = read_export(SET / run), read_export(V8 / run)
        assert [(b["digest"], b["at"]) for b in nine.incidents] == [(b["digest"], b["at"]) for b in eight.incidents], run
        strip = ("wallClockAt",)
        assert ([{k: v for k, v in s.items() if k not in strip} for s in nine.searches]
                == [{k: v for k, v in s.items() if k not in strip} for s in eight.searches]), run


def _attempted(basis):
    """시도 실패 인시던트(`unresolved: false`)에 선 `REWORK` — 판 9 의 새 값 조합. 판 9 세트의 줄에서 판단만 바꾼다."""
    row = dict(read_export(SET / "run-3").incidents[0], unresolved=False)
    row["resolution"] = {"decision": "REWORK", "at": READ_AT, "wallClockAt": "2026-11-15T00:00:00Z",
                         "decidedBy": {"id": "op-1", "kind": "PERSON"}, "reworkBasis": basis}
    return row


def _slot(slot, occupied, identity=None, observed=None):
    return {"slotId": slot, "occupied": occupied, "identity": identity, "observedAt": observed}


def test_재작업_근거는_관측값이_확인을_말할_때만_확인으로_실린다():
    """빈손(`HOLD_KIND_EMPTY`) · 출발의 자재(`occupied: true`) · 빈 목적지(`occupied: false`)만 확인이고 관측 시각을 단다 — 손은
    `readAt`, 자리는 `observedAt` 이 있으면 그것. 출발 신원이 널이면 「모름」으로 적혀 그 자재의 확인으로 읽히지 않는다."""
    full = {"robotId": "hum-02", "hold": {"kind": "HOLD_KIND_EMPTY", "objectRef": None},
            "source": _slot("SEQ-IN-02.BIN-A", True, "ENGINE-COVER-A", "2026-09-06T00:00:02Z"),
            "destination": _slot("RACK-204.S01", False), "readAt": READ_AT}
    query = compose(_attempted(full))
    assert query.facts["resolution"]["reworkChecked"] == {
        "robotHandFree": {"robotId": "hum-02", "at": READ_AT},
        "sourceOccupied": {"slotId": "SEQ-IN-02.BIN-A", "identity": "ENGINE-COVER-A", "at": "2026-09-06T00:00:02Z"},
        "destinationVacant": {"slotId": "RACK-204.S01", "at": READ_AT},
    }
    assert query.facts["unresolved"] is False and query.facts["resolution"]["decision"] == "REWORK"

    unknown = dict(full, source=_slot("SEQ-IN-02.BIN-A", True))
    checked = compose(_attempted(unknown)).facts["resolution"]["reworkChecked"]
    assert checked["sourceOccupied"] == {"slotId": "SEQ-IN-02.BIN-A", "identity": None, "at": READ_AT}
    assert '"sourceOccupied":{"slotId":"SEQ-IN-02.BIN-A","identity":"모름"' in compose(_attempted(unknown)).text


def test_침묵과_묻지_않음과_관측_없음은_확인도_미확인도_아니다():
    """`occupied: null` 은 설비가 말이 없었던 것이고, 칸이 널이면 묻지 않은 것이며, `{robotId, readAt}` 만 든 근거는 관측
    없음이다 — 어느 것도 확인 사실이 되지 않고 「확인 안 함」이라는 사실도 지어지지 않는다. 확인을 말하지 않는 관측값도 그렇다."""
    silent = {"robotId": "hum-02", "hold": None, "source": _slot("SEQ-IN-02.BIN-A", None),
              "destination": _slot("RACK-204.S01", None), "readAt": READ_AT}
    marker = {"robotId": "quad-01", "hold": None, "source": None, "destination": None, "readAt": READ_AT}
    contrary = {"robotId": "hum-02", "hold": {"kind": "HOLD_KIND_HOLDING", "objectRef": "SEQ-IN-02.BIN-A"},
                "source": _slot("SEQ-IN-02.BIN-A", False), "destination": _slot("RACK-204.S01", True, "ENGINE-COVER-B"),
                "readAt": READ_AT}
    for basis in (silent, marker, contrary):
        query = compose(_attempted(basis))
        assert set(query.facts["resolution"]) == {"decision", "at", "decidedByKind"}
        assert "reworkChecked" not in query.text and READ_AT == query.facts["resolution"]["at"]
    # 손만 확인을 말하면 그것만 선다
    partial = dict(silent, hold={"kind": "HOLD_KIND_EMPTY", "objectRef": None})
    assert compose(_attempted(partial)).facts["resolution"]["reworkChecked"] == {
        "robotHandFree": {"robotId": "hum-02", "at": READ_AT}}


def test_재검사_실패는_태스크_없는_실패로_받고_내지_않았다는_표지를_싣는다(tmp_path):
    """받은 `pick_place` 재작업이 첫 발행 직전 재검사를 못 지나면 태스크 없는 실패 인시던트(`REWORK_RECHECK`, `unresolved:
    false`, `fault` 널)가 열린다. 질의에는 결함이 없고 「내지 않았다」 표지가 실린다 — 기체 실패로 메우지 않는다."""
    folder = tmp_path / "recheck"
    folder.mkdir()
    for name in ("manifest.json", "remedy-searches.jsonl"):
        (folder / name).write_bytes((SET / "run-5a" / name).read_bytes())
    row = dict(read_export(SET / "run-5a").incidents[0], failureClass="REWORK_RECHECK", unresolved=False, fault=None,
               attempt=1, resolution=None)
    (folder / "incidents.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")

    bundle = read_export(folder).incidents[0]
    facts = compose(bundle).facts
    assert facts["reworkNotIssued"] is True and facts["failureClass"] == "REWORK_RECHECK"
    assert "fault" not in facts and facts["unresolved"] is False
    # 다른 분류에는 그 표지가 없다
    assert not any("reworkNotIssued" in compose(b).facts for run in RUNS for b in read_export(SET / run).incidents)
