"""내보내기 판 10 인계 세트(`fixtures/picasso-0.11.0-export-10/`) — 운영 경로가 판 10 번들을 받고, 리비전 제거 사건을 실패 · 취소 ·
완료로 접지 않고 「리비전 N 이 범위에서 뺌」으로 싣는가.

picasso 인계 `revision-removal-10.md`(§15.329)의 「읽는 쪽이 할 일」을 본다. 인계 세트는 시나리오가 그대로라 `revision-removals.jsonl`
이 빈 파일이다 — 사건 한 줄이 든 벌은 picasso 인코더(`LedgerExport.revisionRemovalLine`)의 고정 줄 모양대로 이 계층이 지은 입력으로 본다.
"""

import json
import pathlib
import shutil

import pytest

from composer.query import REVISION_REMOVED, compose
from receiver.export import UnknownSchema, read_export
from receiver.run import once
from receiver.scan import scan
from recorder.store import RecordStore

SET = pathlib.Path(__file__).parent / "fixtures" / "picasso-0.11.0-export-10"
V9 = pathlib.Path(__file__).parent / "fixtures" / "picasso-0.11.0-export-9"
RUNS = ("run-1", "run-2", "run-3", "run-4", "run-5a", "run-5b")

#: picasso `RevisionRemovalTest` 의 고정 줄과 같은 칸 · 같은 차례 — 실행 · 작업 지시 · 기체만 run-5a 의 사건 줄에 맞췄다.
#: 리비전이 버전을 건너뛰어(1 → 3) 차가 1 이 아니고, 뺀 단위 둘 중 하나는 태스크 없는 계획 실패(`FAILED`)다.
REMOVAL = ('{"executionId":"exec-1","jobOrderId":"SEQ-RESTART","robotId":"hum-02","fromVersion":1,"toVersion":3,'
           '"removed":[{"unitId":"A","state":"PENDING"},{"unitId":"B","state":"FAILED"}],'
           '"at":"2026-09-06T00:00:02Z","wallClockAt":"2026-11-16T01:02:08Z"}')


def _ok(query, search_text=None):
    return 200, {"success": True, "data": {"llm_failed": False, "answer": "…", "citations": [{"verified": True}]}}


@pytest.mark.parametrize("run", RUNS)
def test_판_10_세트의_줄마다_설명이_한_건씩_붙고_빈_제거_레지스터는_사실을_세우지_않는다(tmp_path, run):
    """여섯 벌 다 빠지는 줄 없이 한 건씩 적힌다. 레지스터는 빈 파일이고 안내의 수는 0 이라 어느 질의에도 제거 사실이 안 선다."""
    folder = SET / run
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert (manifest["schemaVersion"], manifest["contractSemver"]) == ("10", "0.11.0") and manifest["instanceId"]
    assert manifest["counts"]["revisionRemovals"] == 0 and (folder / "revision-removals.jsonl").read_bytes() == b""
    store = RecordStore(tmp_path / "explanations.jsonl")

    written = once(folder, store, search=_ok)

    counts = manifest["counts"]
    assert written == len(store.load()) == counts["incidents"] + counts["remedySearches"]
    batch = scan(folder, set())
    assert batch.revision_removals == []
    for bundle in batch.incidents:
        assert REVISION_REMOVED not in compose(bundle, removals=batch.revision_removals).facts


def test_판_10_의_요약과_가상_시각과_탐색_줄은_판_9_와_같다():
    """사건 줄 · 탐색 줄의 바이트가 그대로다 — 같은 시드의 `digest` · 가상 시각 · 탐색 줄(실 시계 뺌)이 판 9 세트와 같다."""
    for run in RUNS:
        ten, nine = read_export(SET / run), read_export(V9 / run)
        assert [(b["digest"], b["at"]) for b in ten.incidents] == [(b["digest"], b["at"]) for b in nine.incidents], run
        strip = ("wallClockAt",)
        assert ([{k: v for k, v in s.items() if k not in strip} for s in ten.searches]
                == [{k: v for k, v in s.items() if k not in strip} for s in nine.searches]), run
        assert nine.revision_removals == [], run  # 판 9 에는 이 파일이 없다 — 빈 레지스터로 읽는다


def _with_removal(tmp_path, line=REMOVAL, count=1, version="10"):
    """run-5a 를 옮기고 리비전 제거 사건 줄과 안내의 수를 바꾼 벌."""
    folder = tmp_path / "removal"
    shutil.copytree(SET / "run-5a", folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    manifest["schemaVersion"] = version
    manifest["counts"]["revisionRemovals"] = count
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (folder / "revision-removals.jsonl").write_text(line + "\n" if line else "", encoding="utf-8")
    return folder


def test_리비전_제거_사건은_같은_실행의_질의에_범위에서_뺌으로_실리고_설명은_늘지_않는다(tmp_path):
    """사건 한 줄을 그대로 읽고, 같은 실행의 사건 줄 질의에 「리비전 3 이 범위에서 뺌」 · 지우기 전 버전 · 뺀 단위 id · 가상 시각을
    싣는다. 단위의 상태(`FAILED`)와 실 시계는 안 싣고 조치 단계(`resolution`)에도 넣지 않는다 — 실패 · 취소 · 완료가 아니다. 사건은
    인시던트가 아니라 설명 건수가 늘지 않는다."""
    folder = _with_removal(tmp_path)
    export = read_export(folder)
    assert export.revision_removals == [json.loads(REMOVAL)]

    asked = []
    written = once(folder, RecordStore(tmp_path / "explanations.jsonl"),
                   search=lambda text, search_text=None: (asked.append(text), _ok(text))[1])
    counts = export.manifest["counts"]
    assert written == counts["incidents"] + counts["remedySearches"]

    bundle = export.incidents[0]
    assert bundle["executionId"] == "exec-1"
    facts = compose(bundle, removals=export.revision_removals).facts
    assert facts[REVISION_REMOVED] == [{"scope": "리비전 3 이 범위에서 뺌", "fromVersion": 1, "toVersion": 3,
                                        "removedUnits": ["A", "B"], "at": "2026-09-06T00:00:02Z"}]
    assert "resolution" not in facts
    incident_text = next(text for text in asked if '"scope":"리비전 3 이 범위에서 뺌"' in text)
    assert '"state"' not in incident_text and "2026-11-16T01:02:08Z" not in incident_text
    assert sum('"scope":"리비전 3 이 범위에서 뺌"' in text for text in asked) == 1  # 탐색 줄 질의에는 안 실린다

    # 다른 실행의 사건 줄에는 안 서고, 레지스터를 넘기지 않으면 「뺀 것 없음」도 짓지 않는다
    other = dict(bundle, executionId="exec-2")
    assert REVISION_REMOVED not in compose(other, removals=export.revision_removals).facts
    assert REVISION_REMOVED not in compose(bundle).facts


@pytest.mark.parametrize("line, count, version, match", [
    (REMOVAL, 0, "10", "counts.revisionRemovals"),
    (REMOVAL.replace('"state":"FAILED"', '"state":"DONE"'), 1, "10", "removed 의 항목"),
    (REMOVAL.replace('"toVersion":3', '"toVersion":1'), 1, "10", "toVersion 은 fromVersion 보다 크다"),
    (REMOVAL.replace('"fromVersion":1', '"fromVersion":"1"'), 1, "10", "정수"),
    (REMOVAL.replace('"removed":[{"unitId":"A","state":"PENDING"},{"unitId":"B","state":"FAILED"}]', '"removed":[]'),
     1, "10", "비지 않은 배열"),
    (REMOVAL.replace(',"wallClockAt":"2026-11-16T01:02:08Z"', ''), 1, "10", "wallClockAt"),
    (REMOVAL, 1, "9", "들 수 없다"),
])
def test_리비전_제거_레지스터의_모양이_어긋나면_멈춘다(tmp_path, line, count, version, match):
    """안내의 수와 줄 수, 줄의 여덟 칸과 값의 모양을 대조한다. 판 9 이하의 벌이 사건 줄을 실어 오면 형식이 어긋난 것이다."""
    with pytest.raises(UnknownSchema, match=match):
        read_export(_with_removal(tmp_path, line, count, version))


def test_판_10_의_벌에_제거_레지스터가_없으면_멈춘다(tmp_path):
    """picasso 는 판 10 의 벌마다 이 파일을 쓴다(빈 파일이어도). 없음은 판 9 이하에서만 「사건 없음」이다."""
    folder = _with_removal(tmp_path, line="", count=0)
    assert read_export(folder).revision_removals == []
    (folder / "revision-removals.jsonl").unlink()
    with pytest.raises(UnknownSchema, match="revision-removals.jsonl 가 없다"):
        read_export(folder)
