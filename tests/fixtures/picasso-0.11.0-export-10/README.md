# picasso 인계 세트 (계약 0.11.0 · 내보내기 버전 10)

2026-11-16 picasso 가 리비전 제거 사건(§15.329)으로 다시 낸 인계 번들 네 세트(run-1~run-4)와 재기동 장면 한 벌(run-5a · run-5b)이다. 출처는 picasso 저장소 `handoff/narrator/`(main `6c4143d` 시점)이고 `git cat-file blob` 으로 바이트 그대로 옮겼다.
기계가 읽는 파일만(run-*/ 의 incidents.jsonl · remedy-searches.jsonl · revision-removals.jsonl · manifest.json, entitlements.json, ground-truth.jsonl) 들였고, 안내문 `revision-removal-10.md` 는 들이지 않는다. 읽을 일이 있으면 저쪽 원본을 읽는다. `entitlements.json` · `ground-truth.jsonl` 은 버전 9 세트(`picasso-0.11.0-export-9/`)와 같은 바이트다.

| | |
|---|---|
| run-1 ~ run-5b | 버전 9 세트와 같은 장면. `digest` · 가상 시각 · 탐색 줄이 같고 실 시계 · `runId` · `instanceId`(와 그것을 품은 `incidentKey`)만 다르다. 셋째 레지스터 `revision-removals.jsonl` 은 빈 파일이고 안내의 `counts.revisionRemovals` 는 0 이다 — 시나리오에 항목을 빼는 리비전이 없다 |

**읽을 때 지킬 것.**
- 리비전 제거 사건은 실패 · 취소 · 완료가 아니다 — 인시던트를 열지 않고 사람의 판단도 아니다. 같은 실행의 사건 줄 질의에 「리비전 N 이 범위에서 뺌」으로만 싣는다(`composer/query.py` `REVISION_REMOVED`)
- 뺀 단위의 `state`(`PENDING` | `FAILED`)는 지울 때의 상태이지 결과가 아니다. 질의에 안 싣는다
- 버전 9 이하의 벌에는 이 파일이 없다 — 빈 레지스터로 읽는다. 버전 10 의 벌에 파일이 없으면 멈춘다

`tests/test_fixtures_export_10.py` 에서 운영 경로(`receiver.run.once`)가 여섯 벌의 줄마다 설명을 한 건씩 적고, 요약이 버전 9 세트와 같으며, 사건 한 줄이 든 벌(picasso `RevisionRemovalTest` 고정 줄 모양대로 이 계층이 지은 입력)이 같은 실행의 질의에 위 규칙대로 실리고 모양이 어긋나면 멈추는지 시험한다. 측정 기준 세트는 `tests/fixtures/picasso/` 그대로이고 골든셋의 짝도 그 세트의 줄 그대로다.
