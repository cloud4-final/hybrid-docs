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

- 결정은 `decisions.md`의 해당 파트 섹션 맨 위에 한 줄로 추가한다.
  형식: `- **YYYY-MM-DD · 결정** — 이유. (영향: 파트) [출처]`
- 바뀐 결정은 지우지 않는다. `~~기존 결정~~ → YYYY-MM-DD 결정으로 대체`로 표시한다.
  AI는 raw 파일만 읽고 Git 이력을 보지 않으므로, 예전 결정이 다시 쓰이지 않게 파일 안에 남긴다.
- IP 주소는 앞 두 자리만 쓰고 뒤 두 자리는 `x`로 가린다(`10.10.x.x`, `54.116.x.x`). 역할 끝자리처럼 규칙인 부분만 `10.10.x.110`으로 둔다. 예외는 표준 대역·공용 주소(`100.64.0.0/10`, `1.1.1.1`)다. 정확한 값은 Confluence(내부)에 둔다. CI가 가리지 않은 IP를 검사한다.
- 비밀번호, 키, 계정 비밀값은 적지 않는다.
- 아직 정하지 않은 값은 `> 결정 필요(구현 전): …`로 표시한다. 그 값에 의존하는 구현은 결정 뒤에 한다.
- 파트 내부의 세부 설계, 작업 기록, 일지는 여기에 두지 않는다.

## 읽는 곳

- GitHub: 이 repo의 main
- Confluence: `0. 공통 기준` (평일 09·13·18시 자동 갱신, 직접 수정 금지. 1차 구축 중)
- AI: 각 코드 repo의 `AGENTS.md`가 아래 raw URL을 읽게 한다.
  - `https://raw.githubusercontent.com/cloud4-final/hybrid-docs/main/contracts.md`
  - `https://raw.githubusercontent.com/cloud4-final/hybrid-docs/main/decisions.md`
