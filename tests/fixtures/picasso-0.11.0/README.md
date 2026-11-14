# picasso 인계 세트 (계약 0.11.0 · 내보내기 버전 7)

2026-11-14 picasso 가 남이 쥔 기체의 조치 제안을 막고(§15.319) 운영자 취소와 발신자 거부 뒤 회복을 판단 칸에 실으며(§15.320) 다시 낸 인계 번들 네 세트(run-1~run-4)다. 출처는 picasso 저장소 `handoff/narrator/`(picasso main `fde49d1` 시점)이고 `git cat-file blob` 으로 바이트 그대로 옮겼다.
기계가 읽는 파일만(run-*/ 의 incidents.jsonl·remedy-searches.jsonl·manifest.json, entitlements.json, ground-truth.jsonl) 들였고, 안내문 `occupied-live-remedy.md` · `hold-refusal-recovery.md` · `approve-flag.md` 는 들이지 않는다. 읽을 일이 있으면 저쪽 원본을 읽는다.

| | |
|---|---|
| run-1 · run-2 | 사건 10 · 탐색 4 씩(`FOUND` · `NONE` · `WITHHELD` · `SOURCE_MISSING`). `hum-02` 에 랙의 `GRASP_FAILED` 사건(`incident-1`)이 먼저 서고 운영자 취소(`OPERATOR_CANCEL`)로 닫힌 뒤 탐색 `FOUND` 가 선다. 그 뒤 승인된 조치가 깨진 `PAYLOAD_LOST`(`incident-2`)는 앞 버전의 G1 꼴 그대로다. `hum-04` 의 사건(`incident-3`)도 운영자 취소로 닫히고 탐색 `WITHHELD` 보다 앞선다. 사건 번호가 하나씩 밀려 정답 데이터가 `incident-4·7·8·9` 에서 `incident-5·8·9·10` 으로 옮겼다(정지 코드는 그대로) |
| run-3 | 사건 4 · 탐색 0. 버전만 7 로 바뀌었다 |
| run-4 | 사건 3 · 탐색 2. 셋째 모양 — 사건 → 사람의 운영자 취소 → 탐색. `hum-02` · `hum-04` 의 사건에 `OPERATOR_CANCEL` 이 실리고 그 `at` 은 사건 뒤 · 탐색 앞이다. 짝 없는 `hum-03` 의 사건은 `resolution: null` 이다. 앞 버전의 `REWORK` 걸음은 없다 |

**읽을 때 지킬 것.**
- `resolution.decision` 이 버전 7 에서 넷이다 — `REWORK` · `CONFIRM_DONE` · `OPERATOR_CANCEL` · `REMEDY_APPLIED`. `REMEDY_APPLIED` 는 「회복 완료」가 아니고 이 세트에는 없다. 모르는 값이 오면 수신기가 멈춘다(`receiver/export.py` `DECISIONS`)
- `resolution: null` 은 「판단을 안 냈다」이지 「사람이 없었다」의 증명이 아니다 — 상위의 취소는 누가 했는지가 없어 안 실린다
- 탐색 `FOUND` 를 「승인할 수 있다」로 읽지 않는다. 다른 실행이 그 기체를 쥔 채 거절된 경우 `FOUND` 인데 승인할 제안이 없을 수 있고, 승인 가능 여부는 승인 시도의 답(`NO_PROPOSAL` 등)이 정한다. 이 세트에는 그런 줄이 없다

`tests/test_fixtures_contract_0_10.py` 에서 운영 경로(`receiver.run.once`)가 이 세트의 줄마다 설명을 한 건씩 적고 질의에 contractSemver 0.11.0 과 판단 걸음이 번들 값 그대로 실리는지 시험한다. 셋째 모양은 `tests/test_goldenset.py` 의 사람의 걸음 시험이 이 세트로 본다.
측정 기준 세트는 기존 `tests/fixtures/picasso/` 에 둔 채로 유지하며, 골든셋 G1 · G10 · G11 의 짝도 그 세트의 줄 그대로다. 측정 기준과 골든셋의 짝을 새 세트로 옮기는 일은 다음에 실측을 다시 돌릴 때 함께 한다.
