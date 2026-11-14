"""계약 0.10.0 · 0.11.0 인계 세트 — 운영 경로가 새 세트를 그대로 받는가.

측정 기준 세트(`fixtures/picasso/`, 계약 0.9.0 · 스키마 5)는 과거 측정 기록과 incident-recovery 사본이 바이트로
기대고 있어 그대로 둔다. 이 세트들은 그 옆에서 **운영이 picasso 가 내는 번들을 받는지**만 본다 — 0.10.0 은 스키마 6,
0.11.0(2026-11-14)은 지금 picasso 가 내는 스키마 7 이다. 받는 버전마다 실물 한 세트를 둔다.
"""

import json
import pathlib

import pytest

from composer.query import compose
from recorder.store import RecordStore
from receiver.run import once
from receiver.scan import scan

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
#: 세트 폴더와 그 세트가 밝히는 `(schemaVersion, contractSemver)`.
SETS = {"picasso-0.10.0": ("6", "0.10.0"), "picasso-0.11.0": ("7", "0.11.0")}
RUNS = ("run-1", "run-2", "run-3", "run-4")


def _ok(query, search_text=None):
    return 200, {
        "success": True,
        "data": {"llm_failed": False, "answer": "…", "citations": [{"verified": True}]},
    }


@pytest.mark.parametrize("run", RUNS)
def test_새_세트의_줄마다_설명이_한_건씩_붙는다(tmp_path, run):
    """스키마 6 · 7 번들도 빠지는 줄 없이 한 건씩 적힌다. 질의에는 계약 버전이 번들 값 그대로 실린다.

    스키마 7 의 판단 값(`OPERATOR_CANCEL`)은 결정과 가상 시각만 추려 질의에 사실로 실린다 — 값을 풀어 쓰지도 빼지도 않는다."""
    for name, (schema, semver) in SETS.items():
        folder = FIXTURES / name / run
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        assert (manifest["schemaVersion"], manifest["contractSemver"]) == (schema, semver)
        store = RecordStore(tmp_path / name / "explanations.jsonl")
        store.path.parent.mkdir(parents=True, exist_ok=True)

        written = once(folder, store, search=_ok)

        counts = manifest["counts"]
        assert written == len(store.load()) == counts["incidents"] + counts["remedySearches"], name
        batch = scan(folder, set())
        facts = [compose(b).facts for b in batch.incidents]
        assert all(f["contractSemver"] == semver for f in facts), name
        for bundle, fact in zip(batch.incidents, facts):
            step = bundle.get("resolution")
            if step is None:
                assert "resolution" not in fact, name
            else:
                assert fact["resolution"] == {"decision": step["decision"], "at": step["at"]}, name
