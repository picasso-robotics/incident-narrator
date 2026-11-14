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
    for unknown in ("4", "8", 6):
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
