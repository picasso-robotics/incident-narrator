"""번들 읽기 — `BOUNDARY.md` §3.2 의 적재 규약."""

import json
from dataclasses import dataclass

MANIFEST = "manifest.json"
INCIDENTS = "incidents.jsonl"
SEARCHES = "remedy-searches.jsonl"


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
#: **아는 버전만 받는다.** 범위로 받으면 모르는 버전을 아는 척 읽게 되고, 그때 어긋난 칸이
#: 이 계층에서는 「값이 없다」로 보인다 — 형식이 바뀐 것과 관측이 없는 것이 같은 모양이 된다.
SCHEMA_VERSIONS = ("5", "6", "7", "8")

#: 버전마다 사건 줄 `resolution.decision` 이 들 수 있는 값(picasso `docs/glossary.md` §7 · 인계 `hold-refusal-recovery.md`).
#: 5 · 6 은 `REWORK` · `CONFIRM_DONE` 둘이고 7 에서 둘이 더해졌다. `resolution` 이 null 이거나 `decision` 키가 없는
#: 줄은 대조하지 않는다 — 앞은 「판단을 안 냈다」이고 뒤는 질의가 이미 빈 사실로 안 싣는다.
DECISIONS = {
    "5": ("REWORK", "CONFIRM_DONE"),
    "6": ("REWORK", "CONFIRM_DONE"),
    "7": ("REWORK", "CONFIRM_DONE", "OPERATOR_CANCEL", "REMEDY_APPLIED"),
    "8": ("REWORK", "CONFIRM_DONE", "OPERATOR_CANCEL", "REMEDY_APPLIED"),
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
    if problems:
        raise UnknownSchema(f"판 {found} 의 모양이 아니다: {problems}")
    return Export(
        incidents=incidents,
        searches=searches,
        manifest=manifest,
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
    if version != "8":
        return found
    if manifest is not None and not (isinstance(manifest.get("instanceId"), str) and manifest["instanceId"]):
        found.append("manifest: instanceId 가 없다")
    for row in incidents:
        if isinstance(row, dict):
            found.extend(f"{row.get('incidentId')}: {p}" for p in _incident_8(row))
    return found


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
