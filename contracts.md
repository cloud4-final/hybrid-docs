# 공통 기준 · 파트 간 계약

팀 전체가 같은 값으로 맞춰야 하는 것만 적는다. 값을 바꾸려면 이 파일을 고치는 PR을 먼저 올리고 팀원 1명의 승인을 받는다.

## 요약
- 대역: 거점 VM 10.10/10.20/10.30.x.x/24, 거점 DB 10.11/10.21/10.31.x.x/24, AWS VPC 10.200.x.x/16, Tailscale 100.64.0.0/10
- 거점 VM 끝자리: cp `.110`, app `.121`(A만 `.122` 추가)는 VM 대역, data `.130`은 DB 대역
- DB: PostgreSQL, A 원본 `10.11.x.130:5432`, B·C 비동기 streaming 사본
- 사용자 경로: AWS 입구(HAProxy) → 거점 app VM 80/443. cp VM과 DB는 외부에 노출하지 않음
- 거점 식별자: `jammy-a`, `jammy-b`, `jammy-c`, `jammy-obs` (label `site`, env `SITE_ID`에 같은 값)
- collector API: 포트 `8000`, `/api/v1/events`(POST·GET), `/healthz`, `/ready`, `/metrics`. `region`은 `site-a` 형식(`SITE_ID`의 `jammy-a`와 다름)
- 관측 label: `site`, `layer`, `vantage`, `target_site`. 고유 ID(`event_id`, `vehicle_id`, `trace_id`)는 label 금지
- AWS 리소스 태그 필수: `Project`, `Part`, `Owner`, `ManagedBy`, `Name`. `Component`는 정해진 값만
- IP는 앞 두 자리만 공개한다(`10.10.x.x`). 정확한 값은 Confluence(내부). 새 대역·포트는 이 파일에 먼저 추가한다

## 1. 네트워크 대역

public repo라 IP 주소는 앞 두 자리만 보이고 뒤 두 자리는 `x`로 가린다. 팀원은 규칙으로 유추할 수 있다. 정확한 값은 Confluence 「네트워크 주소·포트 총정리」(팀 내부)에서 확인한다.

| 구분 | 값 | 비고 |
|---|---|---|
| 교실 LAN | 192.168.x.x/22 | 공유기 DHCP라 호스트 주소가 바뀔 수 있음 |
| Tailscale | 100.64.0.0/10 | 표준 CGNAT 대역. 거점·AWS·팀원 PC |
| 거점 VM 대역 (`br-vm`) | A 10.10.x.x/24 · B 10.20.x.x/24 · C 10.30.x.x/24 | 게이트웨이 `.1` |
| 거점 DB 대역 (`br-data`) | A 10.11.x.x/24 · B 10.21.x.x/24 · C 10.31.x.x/24 | 게이트웨이 `.1`. 2026-11-05 적용 |
| AWS VPC | 10.200.x.x/16 (서브넷 a·c 각 /24) | |
| AWS 입구 공인 IP (EIP, 고정) | a 54.116.x.x · c 52.78.x.x | |
| burst | 10.72.x.x | 5주차, 규칙 미정 |
| 메시 MTU | 1280 | 방화벽이 MSS 조정 |

## 2. 거점 VM 주소

끝자리는 역할로 정한다. 같은 역할은 세 거점에서 끝자리가 같다.

| 역할 | A | B | C |
|---|---|---|---|
| cp (k3s API) | 10.10.x.110 | 10.20.x.110 | 10.30.x.110 |
| app (앱·Traefik) | 10.10.x.121, 10.10.x.122 | 10.20.x.121 | 10.30.x.121 |
| data (PostgreSQL) | 10.11.x.130 | 10.21.x.130 | 10.31.x.130 |

VM DNS는 1.1.1.1(공용 DNS)이다. VM이 인터넷으로 나갈 때만 NAT를 하고, 다른 거점·AWS로 갈 때는 VM 주소를 그대로 쓴다.

## 3. 허용 경로

Tailscale ACL과 거점 방화벽(nftables)을 둘 다 통과해야 한다. 아래 표에 없는 통신은 차단하고 기록한다.

| 출발 | 목적지 | 포트 | 용도 |
|---|---|---|---|
| 팀원 PC | 거점 호스트·VM (data VM은 관리용만) | 22, ping | 관리 |
| 거점 호스트·VM | 다른 거점 호스트·VM | 22, ping | 거점 간 관리 (data VM 제외) |
| AWS 입구 (`tag:edge`) | app VM | 80, 443 | 서비스 요청 |
| app VM (A·B·C) | 같은 거점 data VM | 5432 | 앱 DB 접속 (11-05 확인) |
| app VM (A·B·C) | 다른 거점 data VM (쓰기 원본 A, 승격 대비 B·C) | 5432 | 원본 쓰기. 11-03 표에서 허용 |
| data VM, `tag:db` | 다른 거점 data VM, `tag:db` | 5432 | DB 복제 |
| 같은 거점 cp VM | data VM | 5432, 22 | **차단** (망 분리 목적) |
| 같은 거점 app VM | data VM | 22 | **차단** |
| 같은 거점 VM | 거점 호스트(게이트웨이) | 전체 | VM → 호스트 |
| 관리 인스턴스 (`tag:mgmt`) | cp VM | 6443 | Argo CD. ACL만 열림, 거점 방화벽은 아직 차단 |
| 거점 호스트·VM | 관측 노트북 (`tag:obs`) | 전체 → 확정 후 축소 | 로그·지표 push |
| 부하 노트북 (A 유선 직결) | A app VM | 80, 443 | 부하 시험 |

> 결정 필요(구현 전): 망 분리(11-05) 뒤 다른 거점 app VM → A 원본 5432가 실제로 열려 있는지 확인해야 한다. 11-05 기록은 같은 거점 app → DB와 data ↔ data만 확인했다. 함께 정할 것: Pod(CNI) 출발지 주소와 SNAT, collector → 거점 호스트 Alloy OTLP `4318`, `br-data`의 모니터링·백업·fencing 경로(담당 jiwon28, HYE0NWEST).

AWS 입구 보안 그룹은 80, 443, UDP 41641만 연다. 입구 SSH(22)는 열지 않고 SSM으로 접속한다. 새 서비스 포트가 필요하면 이 표에 먼저 추가하고, 네트워크 담당(jiwon28)이 방화벽과 ACL에 반영한다.

## 4. 이름과 태그

- 거점 식별자 `jammy-a`, `jammy-b`, `jammy-c`, `jammy-obs`는 호스트 이름, 관측 label `site`, 앱 env `SITE_ID`에 같은 값으로 쓴다.
- 접속은 IP 대신 이름이나 Tailscale로 한다.
- Tailscale 태그: 거점 호스트 `tag:site`, AWS 입구 `tag:edge`, 관리 인스턴스 `tag:mgmt`, 관측 노트북 `tag:obs`, DB `tag:db`, burst `tag:burst`. 태그는 netadmin(jiwon28, Hongsh6414)만 붙인다.
- 관측 노트북에는 `tag:site`를 붙이지 않는다. 붙이면 모든 거점 SSH 권한까지 받는다.

## 5. collector API

| 항목 | 값 |
|---|---|
| 이미지 | `ghcr.io/cloud4-final/jammy-collector:sha-<commit>` (main merge 시 자동 게시) |
| 컨테이너 포트 | 8000 |
| 필수 env | `DATABASE_URL`(쓰기 원본) |
| 선택 env | `DATABASE_READ_URL`, `SITE_ID`, `DEPLOY_ENV`(`dev`/`stage`/`prod`), `DB_POOL_MIN`, `DB_POOL_MAX`, `OTEL_SERVICE_NAME`(기본 `mobility-collector`), `OTEL_EXPORTER_OTLP_ENDPOINT` |

| 엔드포인트 | 성공 | 실패 |
|---|---|---|
| `POST /api/v1/events` | 신규 201 `accepted`, 중복(같은 `event_id`) 200 `duplicate` | 잘못된 `region` 400, DB 장애 503 |
| `GET /api/v1/events/{event_id}` | 200 | 없음 404, DB 장애 503 |
| `GET /api/v1/events` | 200 `{"items", "count"}` (`received_at DESC, event_id DESC`) | `limit` 범위 초과 422, DB 장애 503 |
| `GET /healthz` | 200 (liveness) | 응답 없음 |
| `GET /ready` | 200 (readiness) | DB 연결 실패 503 |
| `GET /metrics` | 200 (Prometheus) | |

- 요청 필드: `event_id`, `region`, `vehicle_id`, `speed_kmh`, `payload`
- **`region` 허용 값은 `aws`, `site-a`, `site-b`, `site-c`다.** 거점 식별자 `SITE_ID`(`jammy-a` 등)와 값이 다르다. 섞어 쓰면 400이 난다.
- `payload` 원문은 로그에 남기지 않는다.
- 승격 때는 코드를 바꾸지 않고 K8s Secret의 `DATABASE_URL`·`DATABASE_READ_URL`만 바꾼다.

> 결정 필요(구현 전): HAProxy 상태 확인은 app VM의 `GET /`(80)이다. Traefik이 컨테이너 8000으로 연결하는 경로와, HAProxy가 `/healthz`·`/ready` 중 무엇을 볼지 정해야 한다.

## 6. DB

- PostgreSQL. A가 쓰기 원본(`10.11.x.130:5432`)이고 B·C는 비동기 streaming 사본이다.
- 마이그레이션은 쓰기 원본에만 1회 실행한다(`python -m src.migrate`).
- 사본 승격은 기존 원본 격리와 단일 쓰기 원본 확인을 포함한 공동 절차로 한다(담당 HYE0NWEST, jiwon28, daji0713).
- 백업 복원 시험은 아직 하지 않았다. 복구 가능성을 검증했다고 표현하지 않는다.

> 결정 필요(구현 전): DB 이름(README 예시 `mobility`)과 앱 계정 이름(예시 `collector_writer`, `collector_reader`)을 확정해야 한다.

## 7. 관측 label

| label | 값 |
|---|---|
| `site` | `jammy-a`, `jammy-b`, `jammy-c`, `jammy-obs` |
| `layer` | `host`, `vm`, `k8s-node`, `pod`, `app` |
| `vantage` | 관측 시점 거점, 거점 내부 수집은 `""` |
| `target_site` | 블랙박스 프로브 대상 거점 |

`event_id`, `vehicle_id`, `trace_id` 같은 고유 ID는 metric label에 넣지 않는다. 이런 값은 Loki 로그와 Tempo trace로 추적한다.

## 8. 운영 데이터 입력 필드

분석·모델용 운영 로그와 지표는 `site`, `service`, `timestamp`, `run_id`, `request_id`, 단위를 식별할 수 있어야 한다.

> 결정 필요(구현 전): collector와 관측 스택의 실제 로그·지표 schema를 이 필드에 맞출 담당과 시점(YangJunMan, daji0713).

## 9. AWS 리소스 태그

- 모든 AWS 리소스: `Project=jammy`, `Part`, `Owner`, `ManagedBy` (Terraform `default_tags`), 그리고 `Name`
- 비용 할당 태그로 켠 것: `Project`, `Part`, `Owner`, `Name`, `ManagedBy`, `aws:createdBy`
- `Component` 값
  - 사용 중: `edge`(입구), `network`(VPC·서브넷·IGW·라우팅), `ci`(GitHub Actions OIDC 역할, `infra/aws/oidc.tf`)
  - 제안(아직 배분안 단계): `mgmt`, `burst`, `storage`, `dns` 등. 새 값은 이 파일에 먼저 추가한다.

## 10. AI 연동 경계 (daji0713)

- 모델 API: `POST /predictions`, `GET /recommendations/{id}`, `/health/live`, `/health/ready`. **로컬에서만 구현했고 거점에 배포하지 않았다.**
- 모델이 준비되지 않으면 예측값이나 Pod 수를 반환하지 않는다(503).
- LLM이 Pod 수를 만들지 않는다. 운영 변경은 사람이 판단한다.
- 분석 workflow는 오프라인 CLI이고 HTTP endpoint가 없다.

## 출처

Confluence 「네트워크 주소·포트 총정리」(2026-11-03), 「[2026-11-04] 거점 안 망 분리」, 「11-05 · DB 망 분리 및 복제 재연결」, 「01 · 서비스 연동 인수」, 「02 · 운영 데이터 계약」, 「03 · AI 계약」, `jammy-collector`·`jammy-observability` README, `hybrid-5th/infra/aws/providers.tf`·`oidc.tf`, 「AWS 비용 관리 체계」
