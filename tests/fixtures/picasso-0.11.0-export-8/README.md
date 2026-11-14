# picasso 인계 세트 (계약 0.11.0 · 내보내기 버전 8)

2026-11-14 picasso 가 감사 내보내기 묶음(§15.322)으로 다시 낸 인계 번들 네 세트(run-1~run-4)와 재기동 장면 한 벌(run-5a · run-5b)이다. 출처는 picasso 저장소 `handoff/narrator/`(인계 브랜치 `feat/audit-export-bundle`, `fd31c6f` 시점)이고 `git cat-file blob` 으로 바이트 그대로 옮겼다.
기계가 읽는 파일만(run-*/ 의 incidents.jsonl · remedy-searches.jsonl · manifest.json, entitlements.json, ground-truth.jsonl) 들였고, 안내문 `audit-export-8.md` 는 들이지 않는다. 읽을 일이 있으면 저쪽 원본을 읽는다. `entitlements.json` · `ground-truth.jsonl` 은 버전 7 세트(`picasso-0.11.0/`)와 같은 바이트다.

| | |
|---|---|
| run-1 ~ run-4 | 버전 7 세트와 같은 장면. `digest` · 가상 시각 · 탐색 줄이 같고 실 시계 · `runId` · 새 칸만 다르다. 코드 케이퍼빌리티로 돌아 임무 버전과 현장 설정 셋이 널이고 모든 인시던트가 `NEW` 다. 판단이 있는 줄은 `decidedBy` 가 `PERSON` 이다 |
| run-5a | 앞 인스턴스. 인시던트 하나(`NEW`, `hum-02` · `RACK-206.S01` · `GRASP_FAILED`, 판단 없음)와 탐색 셋 `SOURCE_UNOBSERVED` · `DESTINATION_OCCUPIED` · `DESTINATION_UNOBSERVED`. 임무 버전 1 · 현장 설정 버전 3 |
| run-5b | 그 판단 기록으로 다시 지은 인스턴스. 같은 보류를 다시 연 인시던트 하나(`REOPENED`). run-5a 의 인시던트와 같은 `incidentKey` · `firstOpenedAt` 으로 이어지고 `digest` · `instanceId` · `at` 은 다르다. 재실행 쌍이 아니다 |

**읽을 때 지킬 것.**
- 같은 `incidentKey` 는 한 사건이다 — run-5b 의 인시던트는 run-5a 의 것의 재발이 아니다(`receiver/history.py`). 열쇠는 뜯어 읽지 않는다
- `attempt` 는 재발 판정의 재료이지 같은 보류를 잇는 열쇠가 아니다
- `decidedBy.id` 는 감사 칸에서만 읽고 질의에는 `kind` 만 싣는다(`receiver/audit.py`)
- 현장 설정 셋은 봉인 라운드의 값이다 — 과거 근거 기한을 정한 설정이 아니다
- 탐색 새 갈래 셋은 승인 가능한 조치가 아니다(`steps` 키 없음). 출발 미관측은 결품이 아니라 확인 요구다

`tests/test_fixtures_export_8.py` 에서 운영 경로(`receiver.run.once`)가 여섯 벌의 줄마다 설명을 한 건씩 적고, 재기동 장면이 재발로 안 세어지며, 판단자 · 임무 · 설정 · 탐색 갈래가 위 규칙대로 질의와 감사 칸에 실리는지 시험한다. 측정 기준 세트는 `tests/fixtures/picasso/` 그대로이고 골든셋의 짝도 그 세트의 줄 그대로다.
