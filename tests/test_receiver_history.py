"""이 계층이 본 사건 안에서의 재발 — `BOUNDARY.md` §4 「사건 이력」."""

from receiver.export import read_export
from receiver.history import count_recurrence, subject


def _b(robot, cls, unit, at, digest):
    return {"robotId": robot, "failureClass": cls, "unitId": unit, "at": at, "digest": digest}


def test_같은_기체_같은_분류의_앞선_사건을_센다():
    """같은 자리(unitId)까지 같으면 따로 센다 — SOP-05 §6 이 「같은 구간에서 반복」을
    묻는다."""
    prior = [
        subject(_b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:01:00Z", "d1")),
        subject(_b("hum-04", "GRASP_FAILED", "RACK-204.S04", "2026-09-06T00:02:00Z", "d2")),
    ]
    now = _b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:03:00Z", "d3")

    assert count_recurrence(now, prior) == {"sameRobotSameClass": 2, "sameUnitSameClass": 1}


def test_같은_digest_는_재실행이지_재발이_아니다():
    """`digest` 는 시드와 가상 시계에서 나오는 결정적 값이라 같은 시나리오를 다시
    돌리면 그대로 반복된다(§3.4). 그것을 세면 재실행마다 재발이 는다."""
    same = _b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:01:00Z", "d1")

    assert count_recurrence(same, [subject(same), subject(same)]) == {
        "sameRobotSameClass": 0, "sameUnitSameClass": 0,
    }


def test_뒤에_난_사건은_세지_않는다():
    """재발은 앞에 있었던 것이다."""
    later = subject(_b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:09:00Z", "d9"))
    now = _b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:03:00Z", "d3")

    assert count_recurrence(now, [later])["sameRobotSameClass"] == 0


def test_다른_분류는_세지_않는다():
    other = subject(_b("hum-04", "PAYLOAD_LOST", "RACK-204.S03", "2026-09-06T00:01:00Z", "d1"))
    now = _b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:03:00Z", "d3")

    assert count_recurrence(now, [other]) == {"sameRobotSameClass": 0, "sameUnitSameClass": 0}


def _line(kind, at):
    return {"kind": kind, "occurredAt": at}


def test_재기동_뒤_다시_연_인시던트는_앞선_재발로_세지_않는다():
    """⛔ **재기동마다 같은 보류가 인시던트 하나를 더 낸다**(picasso limits §15.222). 그것을
    세면 재기동 횟수만큼 재발이 는다. 다시 연 것은 근거 창의 `RESUME_HOLD_REOPENED` 줄 시각이
    번들 `at` 과 **같은** 것뿐이다 — 다시 연 뒤 근거 창 앞 폭 안에 새로 선 보류도 그 줄을
    싣지만 시각이 달라 진짜 사건이다. 시각은 글자가 아니라 시점으로 견준다."""
    original = _b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:01:00Z", "d1")
    reopened = dict(_b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:02:00.010Z", "d2"),
                    evidenceWindow=[_line("RESUME_RECORD", "2026-09-06T00:02:00.009Z"),
                                    _line("RESUME_HOLD_REOPENED", "2026-09-06T00:02:00.01Z")])
    fresh = dict(_b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:02:05Z", "d3"),
                 evidenceWindow=[_line("RESUME_HOLD_REOPENED", "2026-09-06T00:02:00.01Z")])
    now = _b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:03:00Z", "d4")

    prior = [subject(original), subject(reopened), subject(fresh)]

    assert count_recurrence(now, prior) == {"sameRobotSameClass": 2, "sameUnitSameClass": 2}


def test_실물_두_벌에는_재발이_없다(export_dir):
    """⛔ **픽스처 두 번들에는 같은 로봇·같은 분류가 없다**(2026-09-20 실측). 두 번들은
    digest 까지 같아 재실행이다. 그래서 이 테스트는 0 을 확인하고, 재발이 있는 시나리오는
    picasso 에 요청해 둔 상태다(`correspondence/`)."""
    incidents = (
        read_export(export_dir("run-1")).incidents + read_export(export_dir("run-2")).incidents
    )
    prior = [subject(b) for b in incidents]

    assert all(
        count_recurrence(b, prior) == {"sameRobotSameClass": 0, "sameUnitSameClass": 0}
        for b in incidents
    )


def test_같은_시각의_사건은_서로의_앞이_아니다():
    """⛔ **`at` 은 가상 시계의 초 단위다** — 한 초에 사건이 여럿 들어올 수 있다. 같은 초를
    「앞」으로 세면 둘이 **서로를 앞선 사건으로 세어 둘 다 1 을 싣는다.** 먼저 난 쪽에게는
    거짓이고 그 거짓은 미래에 대한 것이다. 덜 세는 쪽으로 틀린다."""
    first = _b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:01:00Z", "d1")
    second = _b("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:01:00Z", "d2")

    assert count_recurrence(first, [subject(second)]) == {
        "sameRobotSameClass": 0, "sameUnitSameClass": 0,
    }
    assert count_recurrence(second, [subject(first)]) == {
        "sameRobotSameClass": 0, "sameUnitSameClass": 0,
    }


def _v8(robot, cls, unit, at, digest, key, kind="NEW", first=None):
    """판 8 줄 — 정체성 칸을 싣는다. `first` 를 안 주면 처음 선 시각은 `at` 이다(열쇠가 널이면 그것도 널)."""
    row = _b(robot, cls, unit, at, digest)
    row.update(incidentKey=key, openingKind=kind, attempt=0,
               firstOpenedAt=None if key is None else (first or at))
    return row


def test_판_8_은_같은_열쇠를_지금_사건과_과거_목록_모두에서_접는다():
    """⛔ **다시 연 쪽이 지금 사건이면 판 7 까지는 원래 보류를 한 번 셌다**(모듈 머리말 2026-10-18). 판 8 은 같은
    `incidentKey` 를 한 사건으로 접는다 — 지금 사건이 다시 연 것이어도 원래 보류(같은 열쇠)를 안 센다. 과거 목록에서도
    원래 보류와 다시 연 줄이 한 사건이라 뒤에 선 다른 사건에게는 한 번만 앞선다."""
    original = _v8("hum-02", "GRASP_FAILED", "RACK-206.S01", "2026-09-06T00:00:01Z", "d1", "mw-a/incident-1")
    reopened = _v8("hum-02", "GRASP_FAILED", "RACK-206.S01", "2026-09-06T00:00:06Z", "d2", "mw-a/incident-1",
                   kind="REOPENED", first="2026-09-06T00:00:01Z")
    later = _v8("hum-02", "GRASP_FAILED", "RACK-206.S01", "2026-09-06T00:00:09Z", "d3", "mw-b/incident-2")
    prior = [subject(original), subject(reopened), subject(later)]

    assert count_recurrence(reopened, prior) == {"sameRobotSameClass": 0, "sameUnitSameClass": 0}
    assert count_recurrence(later, prior) == {"sameRobotSameClass": 1, "sameUnitSameClass": 1}
    # 원래 보류를 못 본 채 다시 연 줄만 받았어도 그 사건은 처음 선 시각으로 한 번 앞선다
    assert count_recurrence(later, [subject(reopened)]) == {"sameRobotSameClass": 1, "sameUnitSameClass": 1}
    # 다시 연 시각(00:00:06)과 처음 선 시각(00:00:01) 사이에 선 사건에게도 원래 보류는 앞이다
    between = _v8("hum-02", "GRASP_FAILED", "RACK-206.S01", "2026-09-06T00:00:03Z", "d4", "mw-a/incident-2")
    assert count_recurrence(between, [subject(reopened)])["sameRobotSameClass"] == 1
    assert count_recurrence(reopened, [subject(between)])["sameRobotSameClass"] == 0


def test_판_8_의_같은_digest_는_열쇠가_달라도_재실행이다():
    """같은 시드의 재실행은 인스턴스가 달라 열쇠가 다르지만 `digest` 가 같다(판 8 도 요약은 그대로다)."""
    first = _v8("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:01:00Z", "d1", "mw-a/incident-1")
    rerun = _v8("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:01:00Z", "d1", "mw-b/incident-1")
    now = _v8("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:03:00Z", "d3", "mw-b/incident-2")

    assert count_recurrence(now, [subject(first), subject(rerun)])["sameRobotSameClass"] == 1


def test_연결_불명은_접지도_새_사건으로_세지도_않고_따로_표시한다():
    """열쇠 널인 `REOPENED` 는 옛 판 판단 기록으로 다시 연 인시던트의 연결 불명이다. 실행 · 단위 · 분류로 추측해 잇지
    않고, 재기동마다 같은 보류가 널 열쇠 줄을 하나씩 더 낼 수 있어 「널이면 매번 새 사건」으로도 세지 않는다 —
    `linkUnknownSeen` 으로 따로 싣는다. 판 7 까지의 줄에는 이 표지가 안 붙는다."""
    unknowns = [_v8("hum-02", "GRASP_FAILED", "RACK-206.S01", f"2026-09-06T00:00:0{s}Z", f"u{s}", None, kind="REOPENED")
                for s in (2, 4)]
    now = _v8("hum-02", "GRASP_FAILED", "RACK-206.S01", "2026-09-06T00:00:09Z", "d9", "mw-c/incident-1")
    assert all(subject(u)["linkUnknown"] for u in unknowns)

    assert count_recurrence(now, [subject(u) for u in unknowns]) == {
        "sameRobotSameClass": 0, "sameUnitSameClass": 0, "linkUnknownSeen": True}
    # 지금 사건이 연결 불명이어도 표지가 선다 — 원래 보류가 앞선 사건으로 셀 수 있다는 뜻이다
    assert count_recurrence(unknowns[1], [])["linkUnknownSeen"] is True
    # 다른 분류의 연결 불명은 이 셈과 상관없다
    other = _v8("hum-02", "PAYLOAD_LOST", "RACK-206.S01", "2026-09-06T00:00:02Z", "p1", None, kind="REOPENED")
    assert count_recurrence(now, [subject(other)]) == {"sameRobotSameClass": 0, "sameUnitSameClass": 0}
    # 뒤에 선 연결 불명 줄은 표지를 세우지 않는다 — 미래에 대한 사실이 된다
    early = _v8("hum-02", "GRASP_FAILED", "RACK-206.S01", "2026-09-06T00:00:01Z", "e1", "mw-c/incident-0")
    assert "linkUnknownSeen" not in count_recurrence(early, [subject(u) for u in unknowns])
    assert "linkUnknownSeen" not in count_recurrence(_b("hum-02", "GRASP_FAILED", "R", "2026-09-06T00:00:09Z", "x"), [])


def test_판_8_줄은_근거_창의_시각_추정을_안_쓴다():
    """판 8 줄은 다시 연 것을 `openingKind` 로 가른다. 근거 창에 같은 시각의 `RESUME_HOLD_REOPENED` 가 있어도 `NEW` 면
    새 사건이다 — 추정은 열쇠가 없는 판 5 · 6 · 7 줄의 것이다."""
    fresh = dict(_v8("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:02:00Z", "d2", "mw-a/incident-2"),
                 evidenceWindow=[_line("RESUME_HOLD_REOPENED", "2026-09-06T00:02:00Z")])
    assert "reopened" not in subject(fresh)
    now = _v8("hum-04", "GRASP_FAILED", "RACK-204.S03", "2026-09-06T00:03:00Z", "d3", "mw-a/incident-3")
    assert count_recurrence(now, [subject(fresh)])["sameRobotSameClass"] == 1
