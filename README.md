# hybrid-docs

3거점 하이브리드 프로젝트의 팀 공통 기준이다. 사람과 AI 모두 이 repo의 main을 기준으로 작업한다.

| 파일 | 내용 |
|---|---|
| [contracts.md](contracts.md) | 파트 간 통일값: 대역, 주소, 포트, 이름, API, DB, 관측 label, AWS 태그 |
| [decisions.md](decisions.md) | 팀이 승인한 결정 |

## 바꾸는 방법

1. 팀에 먼저 제안한다(회의, 채팅, PR 코멘트).
2. 이 repo에 PR을 올린다. 작은 변경은 GitHub 웹에서 연필 아이콘으로 고쳐도 된다. 자기 AI에게 "hybrid-docs에 반영 PR 올려줘"라고 시켜도 된다.
3. 팀원 1명이 승인하면 merge된다. 승인이 곧 합의 기록이다.
4. 코드 PR 본문에 이 PR 링크를 적는다. 링크한 hybrid-docs PR이 merge되기 전에는 코드 PR의 `docs-link-check`가 실패한다(1차 구축 중).

## 작성 규칙

두 파일은 리뷰 AI가 계속 읽는 문서다. 규칙 1개를 블록 1개로 쓰고, `docs-check`가 형식을 검사한다.

- `contracts.md` 블록: `### C-<분류>-<번호> · 제목` (예: `C-NET-001`)
  - `status: active` 필드: `rule`(MUST / MUST NOT / SHOULD 문장), `scope`(repo·경로), `violation`(위반 예시), `source`
  - `status: open`(아직 정하지 않음) 필드: `rule`(정할 것), `owner`
- `decisions.md` 블록: `### D-<YYYYMMDD>-<번호> · 제목` (예: `D-20261104-01`)
  - 필드: `decision`, `implies`(이 결정 때문에 코드가 지켜야 할 것), `why`(한 줄), `scope`, `status`, `source`
- 바뀐 규칙이나 결정은 지우지 않는다. `status: superseded`와 `by: <새 ID>`를 붙이고 새 블록을 추가한다. AI는 Git 이력을 보지 않으므로 파일 안에 남긴다.
- ID는 한 번 쓰면 바꾸거나 재사용하지 않는다. 다른 블록을 가리킬 때는 ID로 쓴다.
- IP 주소는 앞 두 자리만 쓰고 뒤를 `x`로 가린다(`10.10.x.x`, 역할 끝자리는 `10.10.x.110`). 예외는 표준 값(`100.64.0.0/10`, `1.1.1.1`)이다. 정확한 값은 Confluence(내부)에 둔다.
- 비밀번호, 키, 계정 비밀값은 적지 않는다.
- 파트 내부의 세부 설계, 작업 기록, 일지는 여기에 두지 않는다.

## 읽는 곳

- GitHub: 이 repo의 main
- Confluence: `0. 공통 기준` (평일 09·13·18시 자동 갱신, 직접 수정 금지. 1차 구축 중)
- AI: 각 코드 repo의 `AGENTS.md`가 아래 raw URL을 읽게 한다.
  - `https://raw.githubusercontent.com/cloud4-final/hybrid-docs/main/contracts.md`
  - `https://raw.githubusercontent.com/cloud4-final/hybrid-docs/main/decisions.md`
