# picasso 인계 세트 (계약 0.11.0 · 내보내기 버전 9)

2026-11-15 picasso 가 재작업 일반화(§15.323)로 다시 낸 인계 번들 네 세트(run-1~run-4)와 재기동 장면 한 벌(run-5a · run-5b)이다. 출처는 picasso 저장소 `handoff/narrator/`(인계 브랜치 `feat/rework-generalize`, `f1dfd94` 시점)이고 `git cat-file blob` 으로 바이트 그대로 옮겼다.
기계가 읽는 파일만(run-*/ 의 incidents.jsonl · remedy-searches.jsonl · manifest.json, entitlements.json, ground-truth.jsonl) 들였고, 안내문 `rework-generalized.md` 는 들이지 않는다. 읽을 일이 있으면 저쪽 원본을 읽는다. `entitlements.json` · `ground-truth.jsonl` 은 버전 8 세트(`picasso-0.11.0-export-8/`)와 같은 바이트다.

| | |
|---|---|
| run-1 ~ run-5b | 버전 8 세트와 같은 장면. `digest` · 가상 시각 · 탐색 줄이 같고 실 시계 · `runId` · `instanceId`(와 그것을 품은 `incidentKey`) · 근거 칸만 다르다. 판단이 있는 줄마다 `resolution.reworkBasis` 키가 있고 전부 널이다 — 이 시나리오들에는 시도된 실패의 재작업이 없다(run-3 의 `REWORK` 는 보류의 판단이라 근거가 널이다) |

**읽을 때 지킬 것.**
- 근거에서 확인으로 싣는 것은 칸이 있고 관측값이 확인을 말할 때뿐이다 — 빈손(`HOLD_KIND_EMPTY`) · 출발 `occupied: true` · 목적지 `occupied: false`(`composer/query.py` `REWORK_CHECKED`)
- `occupied: null` 은 설비 침묵이지 빈 자리가 아니고, `{robotId, readAt}` 만 든 근거는 관측 없음이다 — 확인도 「확인하지 않았다」도 아니다
- 재검사 실패(`REWORK_RECHECK`)는 내지 않은 시도이고 기체 실패가 아니다. 이 세트에는 그런 줄이 없다

`tests/test_fixtures_export_9.py` 에서 운영 경로(`receiver.run.once`)가 여섯 벌의 줄마다 설명을 한 건씩 적고, 요약이 버전 8 세트와 같으며, 근거의 확인 · 침묵 · 관측 없음과 재검사 실패가 위 규칙대로 질의에 실리는지 시험한다(값이 있는 근거와 재검사 실패 줄은 인계 노트의 모양대로 이 계층이 지은 입력). 측정 기준 세트는 `tests/fixtures/picasso/` 그대로이고 골든셋의 짝도 그 세트의 줄 그대로다.
