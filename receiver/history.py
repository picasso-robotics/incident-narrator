"""이 계층이 본 사건 안에서의 재발 — `BOUNDARY.md` §4 「사건 이력」.

**세는 것이지 판정하는 것이 아니다.** 같은 로봇·같은 분류(그리고 같은 자리·같은 분류)가
이 계층이 본 것 안에서 몇 번 있었나를 센다. 해석은 문서의 것이고 여기서 하지 않는다 — 수를
실으면 근거가 그것을 받는다.

⛔ **코퍼스의 해석이 하나가 아니다 (2026-09-20 실측).** 두 문서가 같은 첫 구절로 다른 결론을
낸다 — SOP-05 §6 은 「한 번은 사건이고, 반복은 **환경의 문제**다」, SOP-04 §4 는 「한 번은
사건이고, 반복은 **동선 설계의 문제**다」. 어느 쪽인지는 실패 분류가 정하고 그 표는 각 문서의
§2 에 있다. **그러니 이 계층이 수에 말을 붙이면 둘 중 하나를 고르는 것이 되고, 그것이 판정이다.**
수만 싣고 고르지 않는다.

**이 계층이 보태는 유일한 사실이다.** 번들에 없고 화면에도 없다. 그래서 이름에 「본 것」이
들어간다(`recurrenceSeen`) — 0 은 「없었다」가 아니라 **「이 층이 본 것 중에는 없다」**다.

**같은 사건의 재실행은 재발이 아니다.** `digest` 는 시드와 가상 시계에서 나오는 결정적
값이라 같은 시나리오를 다시 돌리면 그대로 반복된다(§3.4). 그래서 `digest` 가 다른 것만
세고, 같은 `digest` 는 한 번만 센다. **현재 사건과 같거나 뒤의 것은 안 센다** — 재발은
앞에 있었던 것이다.

⛔ **같은 시각을 「앞」으로 세면 둘이 서로를 센다 (2026-09-20 실측).** `at` 은 picasso 의
가상 시계이고 초 단위라 한 초에 사건이 여럿 들어올 수 있다(픽스처의 `at` 은 이미 1초 간격으로
붙어 있다). 부등호가 엄격하면 같은 초의 두 사건이 **서로를 앞선 사건으로 세어 둘 다 1 을
싣는다** — 먼저 난 쪽에게는 거짓이고, 그 거짓은 **미래에 대한 것**이다. 그래서 같으면 안 센다.
덜 세는 쪽으로 틀린다.

⛔ **재기동 뒤 다시 연 인시던트는 재발이 아니다 (2026-10-18).** picasso 는 재기동마다 같은
보류를 다시 열고 인시던트를 하나 더 낸다(picasso limits §15.222). digest 가 달라 위의 규칙으로는
안 걸러지고, 세면 재기동 횟수만큼 재발이 는다. 가르는 칸은 번들에 없고, 근거 창의
`RESUME_HOLD_REOPENED` 줄 시각이 번들 `at` 과 같은 것만 다시 연 것이다 — 다시 연 뒤 근거 창
앞 폭 안에 새로 선 보류도 그 줄을 싣지만 시각이 다르다. `wallClockAt` 은 따로 읽은 시계라 대지
않는다. **다시 연 쪽이 지금 사건이면 원래 보류를 한 번 센다** — 원래 보류와 잇는 칸이 없어 같은
자리의 진짜 앞선 사건과 가를 수 없다.

⛔ **판 8 부터는 정체성 칸으로 접는다 (2026-11-14, picasso §15.322 · 인계 `audit-export-8.md`).** 사건 줄이 `incidentKey`
(불투명, 같으면 같은 사건)와 `openingKind`(`NEW` | `REOPENED`)를 싣는다. 그래서 판 8 줄에서는 위의 시각 추정(`_reopened`)을
안 쓰고, **같은 `incidentKey` 를 지금 사건과 과거 목록 모두에서 한 사건으로 접는다** — 다시 연 쪽이 지금 사건이어도 원래
보류(같은 열쇠)를 세지 않는다. 판 5 · 6 · 7 줄에는 열쇠가 없어 위의 추정이 여전히 유일한 근거다.

- **앞뒤는 처음 선 시각으로 잰다.** 다시 연 줄의 `at` 은 다시 연 시각이고 사건이 선 것은 `firstOpenedAt` 이다. 그래서 열쇠가
  있는 줄은 지금 사건도 과거 줄도 `firstOpenedAt` 으로 견준다 — 원래 보류를 못 본 채 다시 연 줄만 받았어도 그 사건은 한 번
  센다(같은 열쇠의 다른 줄과는 접힌다).
- **`digest` 도 계속 접는다.** 같은 시드의 재실행은 인스턴스가 달라 열쇠가 다르지만 `digest` 가 같다(판 8 도 요약은 그대로다).
- **연결 불명(열쇠 널인 `REOPENED`)은 접지도 세지도 않는다.** 실행 · 단위 · 분류로 추측해 원래 보류에 잇지 않고, 재기동마다
  같은 보류가 널 열쇠 줄을 하나씩 더 낼 수 있어 「널이면 매번 새 사건」으로도 세지 않는다. 대신 셈에 `linkUnknownSeen` 을
  싣는다 — 같은 기체 · 같은 분류(또는 같은 자리 · 같은 분류)의 연결 불명 줄이 이 층이 본 것 안에서 지금 사건보다 앞에 섰거나
  지금 사건이 그런 줄이면 참이다. 지금 사건이 연결 불명이면 원래 보류가 앞선 사건으로 한 번 셀 수 있다는 표지이기도 하다(가를 칸이 없다).
- **`attempt` 는 잇는 열쇠가 아니다.** 같은 시도에서 미확정과 보류가 각각 인시던트를 열 수 있고, 조치 실패로 선 미발행
  보류는 거부 때 인시던트의 열쇠를 싣는다. 여기서는 읽지 않는다.
"""

#: 재발을 가르는 데 필요한 칸. 이것만 기록에 남긴다 — 번들 전체를 다시 적을 이유가 없다.
#: 판 8 의 정체성 셋(`incidentKey` · `firstOpenedAt` · `openingKind`)도 남긴다 — 지난 번들의 줄도 열쇠로 접으려면 기록에 있어야 한다.
SUBJECT_KEYS = ("robotId", "failureClass", "unitId", "at", "digest", "incidentKey", "firstOpenedAt", "openingKind")

#: 다시 연 인시던트의 표시. 주체와 함께 기록에 남아 지난 번들의 것도 가른다.
REOPENED = "reopened"

#: 판 8 의 연결 불명 — 다시 연 인시던트인데 열쇠가 널이다. 주체와 함께 기록에 남는다.
LINK_UNKNOWN = "linkUnknown"

#: 셈에 붙는 연결 불명 표지. **연결 불명 줄이 끼었을 때만 싣는다** — 없을 때 거짓을 늘 실으면 판 5 · 6 · 7 의 질의가 바뀐다.
LINK_UNKNOWN_SEEN = "linkUnknownSeen"


def subject(bundle):
    """번들에서 주체만. **없는 칸은 안 싣는다** — 널을 값으로 바꾸지 않는다.

    판 8 줄(`openingKind` 키가 있다)은 다시 연 것을 `openingKind` 로 가르고, 판 5 · 6 · 7 줄은 근거 창의 시각으로 추정한다.
    """
    me = {key: bundle[key] for key in SUBJECT_KEYS if bundle.get(key) is not None}
    if "openingKind" in bundle:
        if bundle["openingKind"] == "REOPENED":
            me[REOPENED] = True
            if bundle.get("incidentKey") is None:
                me[LINK_UNKNOWN] = True
    elif _reopened(bundle):
        me[REOPENED] = True
    return me


def _reopened(bundle):
    """근거 창에 시각이 `at` 과 같은 `RESUME_HOLD_REOPENED` 줄이 있나."""
    at = bundle.get("at")
    if not at:
        return False
    return any(
        line.get("kind") == "RESUME_HOLD_REOPENED" and line.get("occurredAt")
        and _instant(line["occurredAt"]) == _instant(at)
        for line in bundle.get("evidenceWindow") or ()
    )


def _instant(text):
    """ISO 시각을 견줄 꼴로. 소수 초 끝의 0 은 같은 시점이다(`.010Z` 와 `.01Z`)."""
    head, _, fraction = text.rstrip("Z").partition(".")
    return head, fraction.rstrip("0")


def _opened(me):
    """사건이 선 시각 — 열쇠가 있으면 처음 선 시각, 없으면 `at`."""
    if me.get("incidentKey") and me.get("firstOpenedAt"):
        return me["firstOpenedAt"]
    return me.get("at")


def _before(other, me):
    """`other` 가 `me` 보다 엄격히 앞에 섰나. 같은 시각은 앞이 아니고, 시각을 모르면 앞으로 친다(판 5 이래의 규칙 그대로)."""
    mine, theirs = _opened(me), _opened(other)
    if not (mine and theirs):
        return True
    return _instant(theirs) < _instant(mine)


def count_recurrence(current, prior):
    """`current` 앞에 같은 로봇·같은 분류 / 같은 자리·같은 분류가 몇 번 있었나.

    :param prior: 주체 사전들 — 저장소가 본 것과 지금 번들의 것을 합친 목록.
    :returns: ``{"sameRobotSameClass": n, "sameUnitSameClass": m}`` — 연결 불명 줄이 끼었으면 ``"linkUnknownSeen": True`` 가 붙는다.
    """
    me = subject(current)
    mine = me.get("incidentKey")
    counted_digests, counted_keys = set(), set()
    same_robot = same_unit = 0
    unknown = bool(me.get(LINK_UNKNOWN))
    for other in prior:
        digest = other.get("digest")
        key = other.get("incidentKey")
        if not digest or digest == me.get("digest") or digest in counted_digests:
            continue
        if other.get("failureClass") != me.get("failureClass"):
            continue
        robot = other.get("robotId") == me.get("robotId")
        unit = bool(other.get("unitId")) and other.get("unitId") == me.get("unitId")
        if other.get(LINK_UNKNOWN):
            # 앞에 선 것만 — 뒤의 줄을 표지로 실으면 미래에 대한 사실이 된다
            unknown = unknown or ((robot or unit) and _before(other, me))
            continue
        if key:
            if key == mine or key in counted_keys:
                continue
        elif other.get(REOPENED):
            continue
        if not _before(other, me):
            continue
        counted_digests.add(digest)
        if key:
            counted_keys.add(key)
        if robot:
            same_robot += 1
        if unit:
            same_unit += 1
    seen = {"sameRobotSameClass": same_robot, "sameUnitSameClass": same_unit}
    if unknown:
        seen[LINK_UNKNOWN_SEEN] = True
    return seen
