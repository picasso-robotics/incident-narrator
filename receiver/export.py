"""번들 읽기 — `BOUNDARY.md` §3.2 의 적재 규약."""

import json
from dataclasses import dataclass, field

MANIFEST = "manifest.json"
INCIDENTS = "incidents.jsonl"
SEARCHES = "remedy-searches.jsonl"
#: 판 10 의 셋째 레지스터(picasso `LedgerExport.REVISION_REMOVALS`). 판 9 이하의 벌에는 없다.
REMOVALS = "revision-removals.jsonl"


#: 이 계층이 읽을 줄 아는 적재 규약의 버전(picasso `LedgerExport.SCHEMA_VERSION`).
#: 내보내는 쪽이 번들마다 싣는 이유가 **읽는 쪽이 멈출 수 있게** 하려는 것이다.
#:
#: ⛔ **3 에서 4 로 올랐다 (2026-09-20).** 사건 줄은 그대로다 — 칸 집합도 `digest` 도
#: 안 바뀌었다. 바뀐 것은 탐색 대장뿐이고 **더해지기만 했다**: `outcome` 에
#: `SOURCE_MISSING` 하위 범주가 생기고, `NONE` 에 `cause`·`unmet` 이, `SOURCE_MISSING` 에
#: `material`·`source`·`observed`·`alternatives` 가 붙었다. 이 계층이 요청한 「점유 축으로
#: 계산된 회복이 인계에 닿게」의 답이다(`correspondence/`).
#:
#: ⛔ **4 에서 5 로 올랐다 (2026-09-23).** 사건 줄에 `resolution` 칸이 는다 — 사람이 그 단위에
#: 낸 판단(`decision` REWORK | CONFIRM_DONE · `at` 가상 시계 · `wallClockAt` 실 시계)이고 내기
#: 전에는 null 이다. 「사람이 안 왔다」와 「왔는데 안 적혔다」를 가르려고 키를 안 뺀다. 요약
#: (`digest`)은 안 바뀐다 — 해시에서 빠지는 것이 `wallClockAt` · `review` · `resolution` 셋이다.
#: 조치 탐색 기록은 그대로다. run-4 의 길(사건 → 사람의 재작업 → 탐색)에서 그 걸음이 안 보여 이 계층이
#: 물었고 picasso 가 실었다(`correspondence/`). 4 는 이제 안 읽는다 — 네 벌을 다 5 로 다시 받았다.
#:
#: ⛔ **5 에서 6 으로 올랐다 (2026-10-08, picasso PR #82 · ADR 50).** 사건 줄의 칸은 그대로다. `route` 에 갈래
#: `SIGNAL`(설비 대기 단위, `intent.unitParameters` 에 `signal` · `expect` · `deadlineSeconds` · `onDeadline`, 기한을
#: 넘기면 `failureClass` 가 `SIGNAL_DEADLINE`)이 더해졌고, 임무 버전이 해시에 들어가 모든 사건의 `digest` 가 바뀌었다.
#: 이 계층은 `route` 로 가르지 않고(질의에 사실로 실을 뿐) `digest` 를 불투명한 식별 값으로만 쓴다. 그래서 5 와 6 을
#: 둘 다 받는다(사용자 결정 2026-10-08). 픽스처(`tests/fixtures/picasso`)와 정답 데이터는 5 그대로다 — 측정 기준선을
#: 흔들지 않으려는 것이다. ⚠ 같은 시나리오의 5 번들과 6 번들은 `digest` 가 달라 한 저장소에 섞이면 재발로 한 번 더 센다.
#:
#: ⛔ **6 에서 7 로 올랐다 (2026-11-14, picasso §15.320 · 인계 `hold-refusal-recovery.md`).** 칸은 그대로이고
#: 사건 줄 `resolution.decision` 이 들 수 있는 값이 둘 늘었다 — `OPERATOR_CANCEL`(사람이 사람 식별자를 든 운영자 취소
#: 입구로 그 실행을 닫았다)과 `REMEDY_APPLIED`(발신자 거부로 선 보류에 사람이 회복 제안을 승인해 조치가 그 단위 앞에
#: 끼었다). ⚠ **`REMEDY_APPLIED` 는 「회복 완료」가 아니다** — 조치와 원래 단위의 결과는 그 뒤의 사건 · 작업 응답이
#: 말한다. 상위의 취소는 누가 했는지가 없어 안 실리므로 `resolution: null` 은 여전히 「판단을 안 냈다」이지 「사람이
#: 없었다」의 증명이 아니다. 해시에서 빠지는 칸이라 `digest` 는 이 이유로는 안 바뀐다. 이 계층은 `decision` 으로
#: 가르지 않고 질의에 결정과 가상 시각을 사실로 옮겨 실을 뿐이라(`composer/query.py` `RESOLUTION_CARRIED`) 값이
#: 느는 것만으로 읽는 법이 안 바뀐다. 다만 **버전마다 아는 값을 적어 두고 모르는 값이 오면 멈춘다**(`DECISIONS`) —
#: 아는 버전을 밝히고 모르는 값을 실은 줄은 형식이 바뀐 것인데, 말없이 옮기면 그 값이 질의에서 사실로 읽힌다.
#:
#: ⛔ **7 에서 8 로 올랐다 (2026-11-14, picasso §15.322 · 인계 `audit-export-8.md`).** 감사 내보내기 묶음이다. 사건 줄에
#: 정체성 넷 — `incidentKey`(불투명, 같으면 같은 사건 · 널은 옛 판 판단 기록으로 다시 연 인시던트의 「연결 불명」) ·
#: `firstOpenedAt`(그 사건이 처음 선 가상 시각) · `openingKind`(`NEW` | `REOPENED`) · `attempt`(봉인 때 시도 번호, 재발 판정의
#: 재료이지 같은 보류를 잇는 열쇠가 아님) — 과 판단자 `resolution.decidedBy {id, kind}`, 의도의 `missionVersion` 과 평평한
#: 현장 설정 셋(`siteSettingsVersion` · `inDoubtGrace` · `stallWindow`, 함께 널이거나 함께 있음)이 붙었다. 탐색 줄 `outcome` 에
#: `SOURCE_UNOBSERVED` · `DESTINATION_OCCUPIED` · `DESTINATION_UNOBSERVED` 셋이 늘었고(셋 다 `steps` 키 없음 · 승인 대상 아님),
#: `manifest.json` 에 `instanceId` 가 붙었다. 새 칸은 해시에서 빠져 **같은 시드의 `digest` 는 판 7 과 같다** — 멱등성 키
#: `(runId, digest)` 그대로다. 읽는 자리: 재발 셈의 접기(`receiver/history.py`), 질의 사실(`composer/query.py`), 판단자 원문의
#: 감사 자리(`receiver/audit.py`). 모양은 `violations` 가 판마다 대조하고 어긋나면 멈춘다.
#:
#: ⛔ **8 에서 9 로 올랐다 (2026-11-15, picasso §15.323 · 인계 `rework-generalized.md`).** 운영자 재작업의 일반화다. 판 8 의 칸은
#: 그대로이고 사건 줄 `resolution` 에 재작업 근거 `reworkBasis` 한 칸이 붙었다 — 판단이 있으면 언제나 키가 있고 값은 널이거나
#: `{robotId, hold, source, destination, readAt}` 이며 **안의 빈 칸도 널로 실린다.** 값은 보류가 아닌 재작업을 받을 때 묶음 뿌리와
#: 물리 게이트를 지난 단위의 `REWORK` 판단에만 있다(`pick_place` 계열은 손 · 출발 · 목적지, 점검 · 이동과 건너뛴 쌍은
#: `{robotId, readAt}` 표지 — 관측 없음). 값 조합도 는다 — 시도 실패 인시던트(`unresolved: false`)에 `REWORK` 가 서고, 첫 발행
#: 직전 재검사를 못 지난 시도는 태스크 없는 실패 인시던트(`failureClass = REWORK_RECHECK`, `fault` 널)를 연다. 판단 칸이라 해시에서
#: 빠져 **같은 시드의 `digest` 는 판 8 과 같다.** 읽는 자리: 질의의 확인 사실(`composer/query.py` `REWORK_CHECKED`)과 재검사 실패
#: 표지(`REWORK_NOT_ISSUED`). 모양은 `violations` 가 대조한다(`_resolution_9`).
#:
#: ⛔ **9 에서 10 으로 올랐다 (2026-11-16, picasso §15.329 · 인계 `revision-removal-10.md`).** 사건 줄 · 탐색 줄의 바이트는 그대로이고
#: **같은 시드의 `digest` 는 판 9 와 같다.** 한 벌에 셋째 레지스터 `revision-removals.jsonl`(빈 파일일 수 있음)이 놓이고 안내
#: `counts` 에 `revisionRemovals`(정수)가 붙었다. 한 줄은 리비전이 작업 지시에서 항목을 빼며 **손대지 않은 단위**(아직 내지 않은
#: `PENDING`, 태스크 없는 계획 실패 `FAILED`)를 실행에서 지운 사건 하나다 — `{executionId, jobOrderId, robotId, fromVersion,
#: toVersion, removed: [{unitId, state}], at, wallClockAt}`. ⚠ **실패 · 취소 · 완료가 아니다** — 인시던트를 열지 않고 사람의 판단도
#: 아니다. 이 계층은 같은 실행의 사건 줄 질의에 「리비전 N 이 범위에서 뺌」으로만 싣는다(`composer/query.py` `REVISION_REMOVED`).
#: 판 9 이하에는 이 파일이 없고 사건도 생기지 않았다 — 없음과 빈 파일을 가르지 않는다(판 9 이하는 빈 목록). 모양은
#: `removal_violations` 가 대조한다.
#:
#: **아는 버전만 받는다.** 범위로 받으면 모르는 버전을 아는 척 읽게 되고, 그때 어긋난 칸이
#: 이 계층에서는 「값이 없다」로 보인다 — 형식이 바뀐 것과 관측이 없는 것이 같은 모양이 된다.
SCHEMA_VERSIONS = ("5", "6", "7", "8", "9", "10")

#: 버전마다 사건 줄 `resolution.decision` 이 들 수 있는 값(picasso `docs/glossary.md` §7 · 인계 `hold-refusal-recovery.md`).
#: 5 · 6 은 `REWORK` · `CONFIRM_DONE` 둘이고 7 에서 둘이 더해졌다. `resolution` 이 null 이거나 `decision` 키가 없는
#: 줄은 대조하지 않는다 — 앞은 「판단을 안 냈다」이고 뒤는 질의가 이미 빈 사실로 안 싣는다.
DECISIONS = {
    "5": ("REWORK", "CONFIRM_DONE"),
    "6": ("REWORK", "CONFIRM_DONE"),
    "7": ("REWORK", "CONFIRM_DONE", "OPERATOR_CANCEL", "REMEDY_APPLIED"),
    "8": ("REWORK", "CONFIRM_DONE", "OPERATOR_CANCEL", "REMEDY_APPLIED"),
    "9": ("REWORK", "CONFIRM_DONE", "OPERATOR_CANCEL", "REMEDY_APPLIED"),
    "10": ("REWORK", "CONFIRM_DONE", "OPERATOR_CANCEL", "REMEDY_APPLIED"),
}

#: 버전마다 탐색 줄 `outcome` 이 들 수 있는 값(picasso `docs/orchestration.md` §6 레지스터의 하위 범주). 판 4 의
#: `SOURCE_MISSING` 까지 넷이고 판 8 에서 셋이 더해졌다. **모르는 값은 멈춘다** — 판단 값과 같은 이유다. 말없이 옮기면
#: 모르는 갈래가 질의에서 사실로 읽히고, 승인 후보 고르기(`receiver/approval.py` `candidates`)는 `FOUND` 만 보므로 조용히 빠진다.
OUTCOMES = {
    "5": ("FOUND", "NONE", "WITHHELD", "SOURCE_MISSING"),
    "6": ("FOUND", "NONE", "WITHHELD", "SOURCE_MISSING"),
    "7": ("FOUND", "NONE", "WITHHELD", "SOURCE_MISSING"),
    "8": ("FOUND", "NONE", "WITHHELD", "SOURCE_MISSING",
          "SOURCE_UNOBSERVED", "DESTINATION_OCCUPIED", "DESTINATION_UNOBSERVED"),
    "9": ("FOUND", "NONE", "WITHHELD", "SOURCE_MISSING",
          "SOURCE_UNOBSERVED", "DESTINATION_OCCUPIED", "DESTINATION_UNOBSERVED"),
    "10": ("FOUND", "NONE", "WITHHELD", "SOURCE_MISSING",
           "SOURCE_UNOBSERVED", "DESTINATION_OCCUPIED", "DESTINATION_UNOBSERVED"),
}

#: `steps` 키가 없어야 하는 갈래 — 승인할 걸음이 없는 응답이다(`WITHHELD` 는 가림, 나머지는 승인할 것이 없음). 이 갈래에
#: `steps` 가 실려 오면 적재면의 방벽이 풀린 것이라 멈춘다.
STEPLESS = ("WITHHELD", "SOURCE_MISSING", "SOURCE_UNOBSERVED", "DESTINATION_OCCUPIED", "DESTINATION_UNOBSERVED")

#: 판 8 사건 줄의 여는 종류(picasso `OpeningKind`)와 판단자의 종류(picasso `ApproverKind`).
OPENING_KINDS = ("NEW", "REOPENED")
DECIDER_KINDS = ("PERSON", "AGENT")

#: 판 8 사건 줄에 키가 있어야 하는 칸 — 값이 널이어도 **키는 빠지지 않는다**(picasso 「없음을 키 누락으로 적지 않는다」).
#: 빠졌으면 그 줄은 판 8 의 모양이 아니다.
IDENTITY_KEYS_8 = ("incidentKey", "firstOpenedAt", "openingKind", "attempt")
INTENT_KEYS_8 = ("missionVersion", "siteSettingsVersion", "inDoubtGrace", "stallWindow")
#: 함께 널이거나 함께 있는 셋(picasso 인코더가 단언). 봉인 라운드의 값이다.
SITE_SETTINGS = ("siteSettingsVersion", "inDoubtGrace", "stallWindow")

#: 판 8 의 모양(정체성 · 판단자 · 의도 · `instanceId`)을 지는 버전들. 판 9 는 판 8 의 칸을 그대로 지고 근거 한 칸을 더한다.
IDENTITY_VERSIONS = ("8", "9", "10")

#: 판 9 의 모양(재작업 근거 · 재검사 실패)을 지는 버전들. 판 10 의 사건 줄은 판 9 와 같은 바이트다.
REWORK_VERSIONS = ("9", "10")

#: 판 10 의 리비전 제거 사건(`revision-removals.jsonl`, picasso §15.329)을 지는 버전들과 그 줄의 칸(picasso
#: `LedgerExport.revisionRemovalLine`). `removed` 의 `state` 는 손대지 않은 단위의 둘뿐이다 — 발행했거나 끝난 단위가 든 항목을
#: 빼는 리비전은 picasso 가 거부해 이 파일에 안 나온다.
REMOVAL_VERSIONS = ("10",)
REMOVAL_KEYS = ("executionId", "jobOrderId", "robotId", "fromVersion", "toVersion", "removed", "at", "wallClockAt")
REMOVED_STATES = ("PENDING", "FAILED")

#: 판 9 의 재작업 근거(`resolution.reworkBasis`, picasso §15.323)에 키가 있어야 하는 칸 — 안의 빈 칸도 널로 실린다(인계
#: `rework-generalized.md`). 손(`hold`)은 `{kind, objectRef}`, 자리(`source` · `destination`)는 `{slotId, occupied, identity,
#: observedAt}` 이고 셋 다 객체 자체가 널이면 묻지 않은 것이다.
REWORK_BASIS_KEYS = ("robotId", "hold", "source", "destination", "readAt")
REWORK_HOLD_KEYS = ("kind", "objectRef")
REWORK_SLOT_KEYS = ("slotId", "occupied", "identity", "observedAt")

#: 판 9 에서 생긴 분류 — 받은 `pick_place` 재작업이 첫 발행 직전 재검사를 못 지나 그 시도를 내지 않고 연 태스크 없는 실패
#: 인시던트(picasso ADR 53 결정 9). `unresolved: false` 이고 `fault` 는 널이다. 앞 판이 이 분류를 실어 오면 형식이 어긋난 것이다.
REWORK_RECHECK = "REWORK_RECHECK"


class UnknownSchema(Exception):
    """모르는 버전이다. **아는 척 읽지 않는다.**

    모르는 버전을 읽으면 필드가 조용히 어긋나고, 그 어긋남이 이 계층에서는 「값이 없다」로
    읽힌다 — 형식이 바뀐 것과 관측이 없는 것이 같은 모양이 된다.
    """


@dataclass(frozen=True)
class Export:
    """번들. **두 대장을 합치지 않는다** — 합치면 하위 범주를 나누는 규칙이 두 곳에 생긴다."""

    incidents: list
    searches: list
    manifest: dict
    #: 판 10 의 리비전 제거 사건(`REMOVALS`). 판 9 이하는 빈 목록이다 — 그 판에서는 사건이 생기지 않았다.
    revision_removals: list = field(default_factory=list)


def read_export(directory):
    """번들을 읽는다. **번들이 아직 아니면 `None`.**

    내보내는 쪽은 임시 파일에 쓰고 이름만 바꾸며, 마지막에 `manifest.json` 이
    나타나는 것이 번들이 다 나왔다는 신호다. 그것이 없는 동안 읽으면 반쯤 쓰인
    파일을 읽는다.

    **없음과 빈 것을 접지 않는다** — `None` 은 「한 벌이 아직 아니다」이고, 기록이
    없는 번들은 빈 번들로 온다.
    """
    manifest_path = directory / MANIFEST
    if not manifest_path.exists():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    found = manifest.get("schemaVersion")
    if found not in SCHEMA_VERSIONS:
        raise UnknownSchema(f"읽을 줄 아는 판은 {list(SCHEMA_VERSIONS)} 인데 {found!r} 가 왔다")
    incidents = _read_lines(directory / INCIDENTS)
    strange = unknown_decisions(found, incidents)
    if strange:
        raise UnknownSchema(f"판 {found} 가 들 수 있는 판단은 {list(DECISIONS[found])} 인데 {strange} 가 왔다")
    searches = _read_lines(directory / SEARCHES)
    problems = violations(found, manifest, incidents, searches)
    removals_path = directory / REMOVALS
    if found in REMOVAL_VERSIONS and not removals_path.exists():
        # picasso 는 판 10 의 벌마다 이 파일을 쓴다(빈 파일이어도) — 없으면 반쯤 쓰인 벌이거나 판이 어긋난 것이다
        problems.append(f"{REMOVALS} 가 없다")
    removals = _read_lines(removals_path)
    problems.extend(removal_violations(found, manifest, removals))
    if problems:
        raise UnknownSchema(f"판 {found} 의 모양이 아니다: {problems}")
    return Export(
        incidents=incidents,
        searches=searches,
        manifest=manifest,
        revision_removals=removals,
    )


def unknown_decisions(version, incidents):
    """그 버전이 들 수 없는 `resolution.decision` 값들(들 수 있는 것뿐이면 빈 목록).

    수신기(`read_export`)와 진단 요청(`diagnose/contract.py`)이 같은 목록으로 막는다 — 두 문이 따로 알면
    한쪽만 새 값을 배운 날 같은 줄이 한 문에서는 사실로, 다른 문에서는 거절로 읽힌다.
    """
    known = DECISIONS.get(version, ())
    found = []
    for row in incidents:
        step = row.get("resolution") if isinstance(row, dict) else None
        if isinstance(step, dict) and "decision" in step and step["decision"] not in known:
            found.append(step["decision"])
    return found


def violations(version, manifest, incidents, searches):
    """그 버전의 모양에서 어긋난 자리들(어긋남이 없으면 빈 목록). 판단 값은 `unknown_decisions` 가 따로 본다.

    수신기(`read_export`)와 진단 요청(`diagnose/contract.py`)이 같은 함수로 막는다 — `unknown_decisions` 와 같은 이유다.
    `manifest` 가 `None` 이면 안내는 대조하지 않는다.

    - 탐색 줄: `outcome` 이 그 버전의 값인가(`OUTCOMES`), 승인할 걸음이 없는 갈래에 `steps` 키가 없는가(`STEPLESS`)
    - 판 8 안내: `instanceId` 가 비지 않은 글자인가
    - 판 8 사건 줄: 정체성 넷의 키가 있고 `openingKind` 가 아는 값이며 `attempt` 가 정수인가. `incidentKey` 와
      `firstOpenedAt` 은 함께 널이고, 널은 `REOPENED` 에만 온다(새로 선 인시던트에는 언제나 값이 있다)
    - 판 8 의도: 네 칸의 키가 있고 현장 설정 셋이 함께 널이거나 함께 있는가
    - 판 8 판단: `resolution` 이 있으면 `decidedBy` 가 `{id, kind}` 이고 `kind` 가 아는 값인가
    - 판 9 는 판 8 의 대조를 다 받고, 판단마다 `reworkBasis` 키가 있으며 값이 널이거나 근거의 모양인가(`_resolution_9`),
      재검사 실패(`REWORK_RECHECK`) 줄이 `unresolved: false` 이고 `fault` 가 널인가. 판 8 까지는 `REWORK_RECHECK` 를 들 수 없다
    - 판 10 의 사건 줄 · 탐색 줄은 판 9 와 같은 대조를 받는다. 리비전 제거 레지스터는 `removal_violations` 가 따로 본다
    """
    found = []
    known = OUTCOMES.get(version, ())
    for row in searches:
        if not isinstance(row, dict):
            continue
        outcome = row.get("outcome")
        if outcome not in known:
            found.append(f"{row.get('searchId')}: 모르는 outcome {outcome!r}")
        elif outcome in STEPLESS and "steps" in row:
            found.append(f"{row.get('searchId')}: {outcome} 에 steps 키가 있다")
    if version not in REWORK_VERSIONS:
        found.extend(f"{row.get('incidentId')}: 판 {version} 은 {REWORK_RECHECK} 를 들 수 없다" for row in incidents
                     if isinstance(row, dict) and row.get("failureClass") == REWORK_RECHECK)
    if version not in IDENTITY_VERSIONS:
        return found
    if manifest is not None and not (isinstance(manifest.get("instanceId"), str) and manifest["instanceId"]):
        found.append("manifest: instanceId 가 없다")
    for row in incidents:
        if isinstance(row, dict):
            found.extend(f"{row.get('incidentId')}: {p}" for p in _incident_8(row))
            if version in REWORK_VERSIONS:
                found.extend(f"{row.get('incidentId')}: {p}" for p in _incident_9(row))
    return found


def removal_violations(version, manifest, removals):
    """판 10 의 리비전 제거 레지스터의 어긋난 자리들(어긋남이 없으면 빈 목록). 수신기(`read_export`)가 부른다.

    - 판 9 이하: 사건이 한 줄이라도 있으면 어긋남이다(그 판은 이 레지스터를 안 낸다)
    - 판 10 안내: `counts.revisionRemovals` 가 정수이고 줄 수와 같은가(`manifest` 가 `None` 이면 안 본다)
    - 판 10 줄: 여덟 칸의 키가 있고, id 셋 · 시각 둘이 비지 않은 글자이며, 버전 둘이 정수이고 `toVersion` 이 더 크며(리비전이
      버전을 건너뛰면 차가 1 이 아니다), `removed` 가 `{unitId, state}` 의 비지 않은 배열이고 `state` 가 `PENDING` | `FAILED` 인가
    """
    if version not in REMOVAL_VERSIONS:
        return [f"판 {version} 은 {REMOVALS} 를 들 수 없다"] if removals else []
    found = []
    if manifest is not None:
        counts = manifest.get("counts")
        count = counts.get("revisionRemovals") if isinstance(counts, dict) else None
        if not _is_int(count):
            found.append(f"manifest: counts.revisionRemovals 가 정수가 아니다: {count!r}")
        elif count != len(removals):
            found.append(f"manifest: counts.revisionRemovals {count} 와 {REMOVALS} 의 줄 수 {len(removals)} 가 다르다")
    for index, row in enumerate(removals, 1):
        found.extend(f"{REMOVALS} {index} 째 줄: {p}" for p in _removal_10(row))
    return found


def _removal_10(row):
    """판 10 리비전 제거 사건 한 줄의 어긋남."""
    if not isinstance(row, dict):
        return [f"객체가 아니다: {row!r}"]
    missing = [k for k in REMOVAL_KEYS if k not in row]
    if missing:
        return [f"{missing} 키가 없다"]
    problems = [f"{key} 는 비지 않은 글자다: {row[key]!r}"
                for key in ("executionId", "jobOrderId", "robotId", "at", "wallClockAt")
                if not (isinstance(row[key], str) and row[key])]
    before, after = row["fromVersion"], row["toVersion"]
    if not (_is_int(before) and _is_int(after)):
        problems.append(f"fromVersion · toVersion 은 정수다: {before!r} · {after!r}")
    elif after <= before:
        problems.append(f"toVersion 은 fromVersion 보다 크다: {before} → {after}")
    removed = row["removed"]
    if not (isinstance(removed, list) and removed):
        problems.append(f"removed 는 비지 않은 배열이다: {removed!r}")
    else:
        for unit in removed:
            if not (isinstance(unit, dict) and isinstance(unit.get("unitId"), str) and unit["unitId"]
                    and unit.get("state") in REMOVED_STATES):
                problems.append(f"removed 의 항목이 {{unitId, state: PENDING | FAILED}} 가 아니다: {unit!r}")
    return problems


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _incident_9(row):
    """판 9 사건 줄 한 줄의 어긋남 — 판 8 의 대조 위에 더하는 것만."""
    problems = []
    if row.get("failureClass") == REWORK_RECHECK:
        if row.get("unresolved") is not False:
            problems.append(f"{REWORK_RECHECK} 는 unresolved: false 다: {row.get('unresolved')!r}")
        if row.get("fault") is not None:
            problems.append(f"{REWORK_RECHECK} 는 태스크가 없어 fault 가 널이다")
    step = row.get("resolution")
    if isinstance(step, dict):
        problems.extend(_resolution_9(step))
    return problems


def _resolution_9(step):
    """판 9 판단 한 건의 재작업 근거 대조. 키가 빠지면 「묻지 않았다」(널)와 「이 판이 안 낸다」가 같은 모양이 된다."""
    if "reworkBasis" not in step:
        return ["resolution 에 reworkBasis 키가 없다"]
    basis = step["reworkBasis"]
    if basis is None:
        return []
    if not isinstance(basis, dict):
        return [f"reworkBasis 는 널이거나 객체다: {basis!r}"]
    if step.get("decision") != "REWORK":
        return [f"reworkBasis 는 REWORK 판단에만 값이 있다: {step.get('decision')!r}"]
    missing = [k for k in REWORK_BASIS_KEYS if k not in basis]
    if missing:
        return [f"reworkBasis 에 {missing} 키가 없다"]
    problems = []
    for key in ("robotId", "readAt"):
        if not (isinstance(basis[key], str) and basis[key]):
            problems.append(f"reworkBasis.{key} 는 비지 않은 글자다: {basis[key]!r}")
    hold = basis["hold"]
    if hold is not None:
        if not (isinstance(hold, dict) and all(k in hold for k in REWORK_HOLD_KEYS)
                and isinstance(hold["kind"], str) and _str_or_none(hold["objectRef"])):
            problems.append(f"reworkBasis.hold 가 {{kind, objectRef}} 가 아니다: {hold!r}")
    for name in ("source", "destination"):
        slot = basis[name]
        if slot is None:
            continue
        if not (isinstance(slot, dict) and all(k in slot for k in REWORK_SLOT_KEYS)
                and isinstance(slot["slotId"], str) and slot["slotId"]
                and (slot["occupied"] is None or isinstance(slot["occupied"], bool))
                and _str_or_none(slot["identity"]) and _str_or_none(slot["observedAt"])):
            problems.append(f"reworkBasis.{name} 가 {{slotId, occupied, identity, observedAt}} 가 아니다: {slot!r}")
    return problems


def _str_or_none(value):
    return value is None or isinstance(value, str)


def _incident_8(row):
    """판 8 사건 줄 한 줄의 어긋남."""
    problems = [f"{key} 키가 없다" for key in IDENTITY_KEYS_8 if key not in row]
    if problems:
        return problems
    kind, key, first = row["openingKind"], row["incidentKey"], row["firstOpenedAt"]
    if kind not in OPENING_KINDS:
        problems.append(f"모르는 openingKind {kind!r}")
    if not isinstance(row["attempt"], int) or isinstance(row["attempt"], bool):
        problems.append(f"attempt 가 정수가 아니다: {row['attempt']!r}")
    if (key is None) != (first is None):
        problems.append("incidentKey 와 firstOpenedAt 은 함께 널이다")
    if key is None and kind != "REOPENED":
        problems.append(f"연결 불명(키 널)은 REOPENED 에만 온다: {kind!r}")
    if key is not None and not (isinstance(key, str) and key):
        problems.append(f"incidentKey 는 비지 않은 글자다: {key!r}")
    intent = row.get("intent")
    if isinstance(intent, dict):
        missing = [k for k in INTENT_KEYS_8 if k not in intent]
        if missing:
            problems.append(f"intent 에 {missing} 키가 없다")
        elif len({intent[k] is None for k in SITE_SETTINGS}) != 1:
            problems.append("현장 설정 셋이 함께 널이거나 함께 있지 않다")
    step = row.get("resolution")
    if isinstance(step, dict):
        decider = step.get("decidedBy")
        if not (isinstance(decider, dict) and isinstance(decider.get("id"), str)
                and decider.get("kind") in DECIDER_KINDS):
            problems.append(f"resolution.decidedBy 가 {{id, kind}} 가 아니다: {decider!r}")
    return problems


def _read_lines(path):
    """줄 단위. 배열이 아니라 줄인 이유는 덧붙이기가 줄 추가로 그대로 옮겨지기 때문이다."""
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
