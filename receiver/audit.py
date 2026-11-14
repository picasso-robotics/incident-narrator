"""판단자 원문의 자리 — 감사 기록과 승인자 연결(picasso 인계 `audit-export-8.md`, ADR 47).

판 8 의 사건 줄 `resolution.decidedBy {id, kind}` 는 같은 줄 `approvedBy` 와 같은 모양이다. **원문 id 를 읽는 곳은 여기
하나다.** 설명 생성 입력(`composer/query.py`)에는 종류(`kind`)만 넘긴다 — id 는 호출자의 주장이지 인증 증명이 아니라서,
질의에 실으면 설명이 그 글자를 「누가 판단했다」는 확인된 사실로 옮긴다.

여기서 하는 일은 둘이다.

- **감사 기록.** 설명 한 건 옆에 그 사건의 판단자 원문을 남긴다(`recorder/record.py` `Record.audit`). 질의에도 코퍼스
  내보내기(`corpus/export.py`)에도 실리지 않는다
- **승인자 연결.** 같은 줄의 승인자(`approvedBy`)와 판단자의 id 가 같은 글자인가 — 같은 사람의 승인과 판단을 잇는다.
  ⚠ 같은 글자라는 것이지 같은 사람이 인증됐다는 것이 아니다. 어느 한쪽이 없으면 `None` 이다 — 「다르다」와 「댈 것이
  없다」를 접지 않는다

판 7 까지의 줄과 판단이 없는 줄에는 판단자가 없어 빈 사전을 돌려준다 — 「판단자 없음」이 아니라 「이 줄에 댈 것이 없다」다.
"""

DECIDER = "decidedBy"
APPROVER = "approvedBy"
SAME_ID = "sameIdAsApprover"


def _party(value):
    """`{id, kind}` 꼴이면 그 둘만 베껴 담고, 아니면 `None`."""
    if isinstance(value, dict) and "id" in value and "kind" in value:
        return {"id": value["id"], "kind": value["kind"]}
    return None


def decision_audit(bundle):
    """사건 줄 하나의 판단자 감사 항목. 판단자가 없으면 빈 사전.

    :returns: ``{"incidentKey", "decision", "decidedBy": {id, kind}, "approvedBy": {id, kind} | None,
        "sameIdAsApprover": bool | None}``
    """
    resolution = bundle.get("resolution") if isinstance(bundle, dict) else None
    if not isinstance(resolution, dict):
        return {}
    decider = _party(resolution.get(DECIDER))
    if decider is None:
        return {}
    approver = _party(bundle.get(APPROVER))
    return {
        "incidentKey": bundle.get("incidentKey"),
        "decision": resolution.get("decision"),
        DECIDER: decider,
        APPROVER: approver,
        SAME_ID: None if approver is None else approver["id"] == decider["id"],
    }
