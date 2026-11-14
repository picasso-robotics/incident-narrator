"""수신기가 번들을 읽는 규율 — `BOUNDARY.md` §3.2."""

import json

import pytest

from receiver.export import UnknownSchema, read_export


def test_manifest가_없으면_한_벌이_아니다(tmp_path):
    """내보내는 쪽이 아직 쓰는 중일 수 있다. 반쯤 쓰인 파일을 읽지 않는다."""
    (tmp_path / "incidents.jsonl").write_text(
        '{"incidentId": "incident-1", "digest": "abc"}\n', encoding="utf-8"
    )
    # manifest.json 이 없다 — 번들이 다 나오지 않았다는 뜻이다

    assert read_export(tmp_path) is None


def test_기록이_없는_한_벌도_한_벌이다(tmp_path):
    """빈 번들과 「한 벌이 아직 아니다」는 다른 상태다. 접으면 구별이 사라진다."""
    (tmp_path / "manifest.json").write_text(
        '{"schemaVersion": "5", "runId": "run-1"}', encoding="utf-8"
    )
    (tmp_path / "incidents.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "remedy-searches.jsonl").write_text("", encoding="utf-8")

    export = read_export(tmp_path)

    assert export is not None
    assert export.incidents == []
    assert export.searches == []


def test_모르는_판은_읽지_않는다(tmp_path):
    """번들마다 `schemaVersion` 이 실린다. 모르는 버전을 아는 척 읽으면 필드가
    조용히 어긋나고, 그 어긋남이 「값이 없다」로 읽힌다 — 멈추는 쪽이 맞다."""
    (tmp_path / "manifest.json").write_text(
        '{"schemaVersion": "99", "runId": "run-1"}', encoding="utf-8"
    )

    with pytest.raises(UnknownSchema):
        read_export(tmp_path)

    # 버전 6(2026-10-08)은 안다 — 사건 줄의 칸은 그대로이고 `route` 에 `SIGNAL` 갈래가 더해졌을 뿐이다.
    # 그 갈래의 줄도 다른 줄과 같은 모양으로 읽힌다. 4 는 이제 안 읽는다.
    (tmp_path / "manifest.json").write_text('{"schemaVersion": "6", "runId": "run-1"}', encoding="utf-8")
    (tmp_path / "incidents.jsonl").write_text(
        '{"incidentId": "incident-1", "digest": "abc", "route": "SIGNAL", "failureClass": "SIGNAL_DEADLINE",'
        ' "intent": {"unitParameters": {"signal": "door", "expect": "OPEN", "deadlineSeconds": 30,'
        ' "onDeadline": "FAIL"}}}\n', encoding="utf-8")
    export = read_export(tmp_path)
    assert export.manifest["schemaVersion"] == "6"
    assert export.incidents[0]["route"] == "SIGNAL" and export.incidents[0]["failureClass"] == "SIGNAL_DEADLINE"
    for unknown in ("4", "9", 6):
        (tmp_path / "manifest.json").write_text(f'{{"schemaVersion": {unknown!r}}}'.replace("'", '"'), encoding="utf-8")
        with pytest.raises(UnknownSchema):
            read_export(tmp_path)

    # 버전 7(2026-11-14)도 안다 — 칸은 그대로이고 `resolution.decision` 에 `OPERATOR_CANCEL` · `REMEDY_APPLIED` 가
    # 더해졌다. 값은 그대로 옮겨진다. 같은 값을 버전 6 이라 밝힌 줄은 형식이 어긋난 것이라 멈춘다 — 말없이 옮기면
    # 그 값이 질의에서 사실로 읽힌다. 모르는 값은 버전 7 에서도 멈추고, null 판단은 대조하지 않는다.
    def lines(*rows):
        return "".join(json.dumps(row) + "\n" for row in rows)

    for decision in ("OPERATOR_CANCEL", "REMEDY_APPLIED"):
        (tmp_path / "incidents.jsonl").write_text(lines(
            {"incidentId": "incident-1", "digest": "abc",
             "resolution": {"decision": decision, "at": "2026-09-06T00:00:04Z"}},
            {"incidentId": "incident-2", "digest": "def", "resolution": None}), encoding="utf-8")
        (tmp_path / "manifest.json").write_text('{"schemaVersion": "7", "runId": "run-1"}', encoding="utf-8")
        export = read_export(tmp_path)
        assert export.incidents[0]["resolution"]["decision"] == decision
        assert export.incidents[1]["resolution"] is None
        (tmp_path / "manifest.json").write_text('{"schemaVersion": "6", "runId": "run-1"}', encoding="utf-8")
        with pytest.raises(UnknownSchema, match=decision):
            read_export(tmp_path)
    (tmp_path / "incidents.jsonl").write_text(lines(
        {"incidentId": "incident-1", "digest": "abc", "resolution": {"decision": "AUTO_RECOVERED"}}), encoding="utf-8")
    (tmp_path / "manifest.json").write_text('{"schemaVersion": "7", "runId": "run-1"}', encoding="utf-8")
    with pytest.raises(UnknownSchema, match="AUTO_RECOVERED"):
        read_export(tmp_path)


def _write(folder, manifest, incidents=(), searches=()):
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (folder / "incidents.jsonl").write_text("".join(json.dumps(r) + "\n" for r in incidents), encoding="utf-8")
    (folder / "remedy-searches.jsonl").write_text("".join(json.dumps(r) + "\n" for r in searches), encoding="utf-8")


def _eight(**changes):
    row = {"incidentId": "incident-1", "digest": "abc", "incidentKey": "mw-1/incident-1",
           "firstOpenedAt": "2026-09-06T00:00:01Z", "openingKind": "NEW", "attempt": 0,
           "intent": {"missionVersion": 1, "siteSettingsVersion": 3, "inDoubtGrace": "PT20S", "stallWindow": "PT40S"},
           "approvedBy": None, "resolution": None}
    row.update(changes)
    return row


MANIFEST_8 = {"schemaVersion": "8", "runId": "run-1", "instanceId": "mw-1"}


def test_판_8_을_받고_모양이_어긋나면_멈춘다(tmp_path):
    """판 8(2026-11-14, picasso §15.322)은 정체성 넷 · 판단자 · 임무 버전 · 현장 설정 셋 · 탐색 갈래 셋 · `instanceId` 를 더한다.
    받되 판마다 모양을 대조한다 — 형식이 바뀐 줄을 말없이 옮기면 어긋난 칸이 「값이 없다」로 읽힌다."""
    reopened = _eight(incidentId="incident-2", digest="def", incidentKey=None, firstOpenedAt=None, openingKind="REOPENED",
                      intent={"missionVersion": None, "siteSettingsVersion": None, "inDoubtGrace": None, "stallWindow": None},
                      resolution={"decision": "REWORK", "at": "2026-09-06T00:00:04Z",
                                  "decidedBy": {"id": "op-1", "kind": "PERSON"}})
    searches = [{"searchId": "search-1", "outcome": "SOURCE_UNOBSERVED", "material": None, "source": "S", "occupied": None},
                {"searchId": "search-2", "outcome": "DESTINATION_OCCUPIED", "destination": "D", "observed": None},
                {"searchId": "search-3", "outcome": "DESTINATION_UNOBSERVED", "destination": "D"}]
    _write(tmp_path, MANIFEST_8, [_eight(), reopened], searches)
    export = read_export(tmp_path)
    assert [r["openingKind"] for r in export.incidents] == ["NEW", "REOPENED"]
    assert [s["outcome"] for s in export.searches] == [s["outcome"] for s in searches]

    broken = {
        "instanceId": ({k: v for k, v in MANIFEST_8.items() if k != "instanceId"}, [_eight()], []),
        "openingKind": (MANIFEST_8, [_eight(openingKind="RESUMED")], []),
        "attempt": (MANIFEST_8, [_eight(attempt="0")], []),
        "함께 널": (MANIFEST_8, [_eight(firstOpenedAt=None)], []),
        "REOPENED 에만": (MANIFEST_8, [_eight(incidentKey=None, firstOpenedAt=None)], []),
        "키가 없다": (MANIFEST_8, [{k: v for k, v in _eight().items() if k != "attempt"}], []),
        "현장 설정 셋": (MANIFEST_8, [_eight(intent={"missionVersion": 1, "siteSettingsVersion": 3, "inDoubtGrace": None,
                                                    "stallWindow": "PT40S"})], []),
        "decidedBy": (MANIFEST_8, [_eight(resolution={"decision": "REWORK", "at": "2026-09-06T00:00:04Z"})], []),
        "steps": (MANIFEST_8, [], [{"searchId": "search-1", "outcome": "DESTINATION_UNOBSERVED", "steps": []}]),
        "DESTINATION_CLEARED": (MANIFEST_8, [], [{"searchId": "search-1", "outcome": "DESTINATION_CLEARED"}]),
    }
    for needle, (manifest, incidents, rows) in broken.items():
        _write(tmp_path, manifest, incidents, rows)
        with pytest.raises(UnknownSchema, match=needle):
            read_export(tmp_path)


def test_판_8_의_탐색_갈래는_판_7_이_들_수_없다(tmp_path):
    """새 갈래 셋을 판 7 이라 밝힌 줄은 형식이 어긋난 것이다. 판단 값과 같은 이유로 멈춘다."""
    for outcome in ("SOURCE_UNOBSERVED", "DESTINATION_OCCUPIED", "DESTINATION_UNOBSERVED"):
        _write(tmp_path, {"schemaVersion": "7", "runId": "run-1"}, [], [{"searchId": "search-1", "outcome": outcome}])
        with pytest.raises(UnknownSchema, match=outcome):
            read_export(tmp_path)
