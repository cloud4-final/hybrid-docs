<!-- confluence-page-id: 17367041 -->
# 공통 기준 · 파트 간 계약

파트 사이에 같은 값으로 맞춰야 하는 규칙이다. 사람과 리뷰 AI가 함께 읽는다. 변경은 hybrid-docs PR에서 팀원 1명이 승인해야 한다.

## 리뷰어 사용법

- 규칙 1개가 블록 1개다. 위반을 찾으면 규칙 ID를 인용한다. 예: `C-API-002 위반: region에 jammy-a 사용`.
- 블록의 `scope`에 해당하는 변경에만 그 규칙을 적용한다.
- `status: active`만 위반으로 판단한다.
  - `status: open`은 아직 정하지 않은 항목이다. 그 값에 의존하는 코드는 "결정 필요"로 표시하고 위반으로 보지 않는다.
  - `status: superseded`는 적용하지 않는다.
- IP의 `x`는 public repo라서 가린 자리다. 코드의 IP가 앞 두 자리나 역할 끝자리(`.110`, `.121`, `.130`)에서 규칙과 다르면 위반이다. `x` 자리 값은 판단하지 않는다.
- 이 파일에 없는 값은 판단하지 않는다. 결정의 이유는 `decisions.md`의 `D-` ID를 본다.
- 표준 값은 가리지 않는다: Tailscale `100.64.0.0/10`, 공용 DNS `1.1.1.1`.

## 네트워크 대역

### C-NET-001 · 거점 VM 대역
- rule: 거점 cp·app VM은 거점 VM 대역(`br-vm`)을 써야 한다(MUST). A 10.10.x.x/24, B 10.20.x.x/24, C 10.30.x.x/24, 게이트웨이 `.1`.
- scope: hybrid-5th(`infra/*`, `k8s/*`, `scripts/*`), jammy-observability(`site/*`, `hub/*`), jammy-collector(`deploy/*`)
- violation: app VM 주소를 10.11.x.121로 지정
- status: active
- source: Confluence 13467672

### C-NET-002 · 거점 DB 대역
- rule: data VM과 PostgreSQL은 DB 대역(`br-data`)만 써야 한다(MUST). A 10.11.x.x/24, B 10.21.x.x/24, C 10.31.x.x/24, 게이트웨이 `.1`.
- scope: DB 주소를 쓰는 모든 설정(`DATABASE_URL`, Secret, 방화벽, 관측 target)
- violation: DB 주소 10.10.x.130 (망 분리 전 주소)
- status: active
- source: D-20261104-01

### C-NET-003 · AWS VPC 대역
- rule: AWS 리소스는 VPC 10.200.x.x/16 안에서 서브넷 a·c(각 /24)를 써야 한다(MUST).
- scope: hybrid-5th `infra/aws/*`
- violation: 새 서브넷을 10.10.x.x로 생성
- status: active
- source: Confluence 13467672

### C-NET-004 · 새 대역
- rule: 새 대역은 기존 대역(10.10·10.20·10.30·10.11·10.21·10.31·10.200·192.168·100.64)과 겹치면 안 된다(MUST NOT). 쓰기 전에 이 파일에 먼저 추가해야 한다(MUST).
- scope: 모든 repo
- violation: 이 파일에 없는 대역 10.40.x.x를 코드에 추가
- status: active
- source: Confluence 13467672

### C-NET-005 · 메시 MTU
- rule: 거점 사이 Tailscale 통신은 MTU 1280을 전제로 한다. 더 큰 MTU를 가정하면 안 된다(MUST NOT).
- scope: hybrid-5th 네트워크 설정, 대용량 전송 설정
- violation: 터널 경로에 MTU 1500 강제
- status: active
- source: Confluence 13467672

### C-NET-006 · burst 대역
- rule: burst 대역(10.72.x.x 예정)과 규칙을 정해야 한다.
- status: open
- owner: jiwon28, Hongsh6414 (5주차)

## 주소 규칙

### C-ADDR-001 · 역할별 끝자리
- rule: 역할마다 끝자리가 고정이다(MUST). cp `.110`, app `.121`(A만 `.122` 추가), data `.130`. 세 거점이 같은 끝자리를 쓴다.
- scope: 거점 VM 주소를 쓰는 모든 설정(HAProxy 목적지, K8s, 관측 target, 방화벽)
- violation: HAProxy 목적지를 10.20.x.122로 추가 (B에는 `.122`가 없음)
- status: active
- source: Confluence 13467672, 16973840

### C-ADDR-002 · 이름 기반 접속
- rule: 사람과 script의 접속은 IP 대신 이름(`jammy-a` 등)이나 Tailscale 이름을 써야 한다(SHOULD). 교실 LAN(192.168.x.x) 주소를 고정값으로 쓰면 안 된다(MUST NOT). DHCP라 바뀐다.
- scope: 모든 repo의 script, 배포 설정
- violation: deploy script에 192.168.x.x 주소를 고정
- status: active
- source: Confluence 13467672

### C-ADDR-003 · VM DNS와 NAT
- rule: VM DNS는 1.1.1.1이다. VM 주소는 다른 거점·AWS로 갈 때 NAT 없이 그대로 보인다. 출발지 IP 기반 규칙은 VM 주소로 써야 한다(MUST).
- scope: 방화벽, DB 접근 규칙(`pg_hba`), 관측 설정
- violation: DB 허용 규칙에 거점 호스트 주소만 등록
- status: active
- source: Confluence 13467672

## 통신 경로

### C-PATH-001 · 서비스 진입
- rule: 사용자 요청은 AWS 입구(HAProxy, `tag:edge`) → app VM 80/443으로만 들어와야 한다(MUST). cp VM과 data VM을 외부에 노출하면 안 된다(MUST NOT).
- scope: hybrid-5th(`infra/aws/*`, HAProxy 설정, `k8s/*`)
- violation: HAProxy 목적지에 cp VM(.110) 추가
- status: active
- source: Confluence 12943383, 13467672

### C-PATH-002 · 앱 → DB
- rule: app VM은 같은 거점 data VM의 5432에 접속한다. 쓰기는 원본 A(10.11.x.130:5432)로 간다. 다른 거점 app VM → 원본 5432 경로가 필요하다.
- scope: jammy-collector(`DATABASE_URL`), hybrid-5th(방화벽, `k8s/*` Secret)
- violation: B app의 `DATABASE_URL`이 10.21.x.130을 쓰기 원본으로 지정
- status: active
- source: Confluence 13467672, 16973840

### C-PATH-003 · DB 복제
- rule: data VM ↔ 다른 거점 data VM(`tag:db`)은 5432로 복제한다. A가 원본이고 B·C는 비동기 streaming 사본이다.
- scope: PostgreSQL 설정, 방화벽
- violation: B·C 사본에 쓰기 설정
- status: active
- source: Confluence 16973840

### C-PATH-004 · DB 차단 경로
- rule: cp VM → data VM 5432·22, app VM → data VM 22, AWS 입구 → data VM은 막아야 한다(MUST). data VM SSH는 팀원 관리 접속만 허용한다.
- scope: hybrid-5th 방화벽·ACL, K8s 설정
- violation: cp VM의 Pod가 DB에 직접 접속하도록 설정
- status: active
- source: D-20261104-01

### C-PATH-005 · 관리 경로
- rule: 팀원 PC → 거점 호스트·VM 22, 거점 ↔ 거점 22(data VM 제외), 같은 거점 VM → 거점 호스트는 허용이다. AWS 입구 보안 그룹은 80, 443, UDP 41641만 열고 SSH(22)를 열면 안 된다(MUST NOT). 입구 접속은 SSM으로 한다.
- scope: hybrid-5th `infra/aws/*`, 방화벽·ACL
- violation: 입구 보안 그룹에 22 inbound 추가
- status: active
- source: Confluence 13467672

### C-PATH-006 · 새 포트
- rule: 위에 없는 새 서비스 포트나 경로는 이 파일에 먼저 추가해야 한다(MUST). 방화벽과 ACL은 네트워크 담당(jiwon28)이 반영한다. 표에 없는 통신은 차단되고 기록된다.
- scope: 모든 repo
- violation: 이 파일에 없는 포트 9000을 서비스 노출에 사용
- status: active
- source: Confluence 13467672

### C-PATH-007 · 망 분리 후 남은 경로
- rule: 다음을 확인하거나 정해야 한다.
  - 망 분리 뒤 다른 거점 app → A 원본 5432가 실제로 열려 있는지
  - Pod(CNI) 출발지 주소와 SNAT
  - collector → 거점 호스트 Alloy OTLP 4318
  - `br-data` 모니터링·백업·fencing 경로
  - 관리 인스턴스(Argo CD) → cp VM 6443을 거점 방화벽에서 열 시점
  - 거점 → 관측 노트북(`tag:obs`) 포트 축소
- status: open
- owner: jiwon28, HYE0NWEST
- source: Confluence 14909445, 16973840, jammy-collector README §5

## 이름과 태그

### C-NAME-001 · 거점 식별자
- rule: 거점 식별자는 `jammy-a`, `jammy-b`, `jammy-c`, `jammy-obs`다. 호스트 이름, 관측 label `site`, 앱 env `SITE_ID`에 같은 값을 써야 한다(MUST).
- scope: 모든 repo
- violation: label `site="A"` 또는 `SITE_ID=site-a`
- status: active
- source: jammy-observability README §2, jammy-collector README §2

### C-NAME-002 · Tailscale 태그
- rule: 장비 태그는 거점 호스트 `tag:site`, AWS 입구 `tag:edge`, 관리 인스턴스 `tag:mgmt`, 관측 노트북 `tag:obs`, DB `tag:db`, burst `tag:burst`다. 관측 노트북에 `tag:site`를 붙이면 안 된다(MUST NOT). 태그는 netadmin(jiwon28, Hongsh6414)만 붙인다.
- scope: Tailscale ACL, AWS user_data
- violation: 새 관리 서버에 `tag:site` 부여
- status: active
- source: Confluence 13467672

## collector API

### C-API-001 · 이미지와 포트
- rule: collector 이미지는 `ghcr.io/cloud4-final/jammy-collector:sha-<commit>`이다(main merge 시 자동 게시). 컨테이너 포트는 8000이다. 배포는 `latest` 대신 `sha-` tag를 써야 한다(MUST).
- scope: hybrid-5th `k8s/*`, jammy-observability `hub/*`(demo), jammy-collector `deploy/*`
- violation: `image: ghcr.io/cloud4-final/jammy-collector:latest`
- status: active
- source: jammy-collector README §1

### C-API-002 · region 값
- rule: 요청 필드 `region`은 `aws`, `site-a`, `site-b`, `site-c` 중 하나여야 한다(MUST). `SITE_ID`(`jammy-a`)와 섞으면 안 된다(MUST NOT). 다르면 400이 난다.
- scope: collector `POST /api/v1/events`를 호출하는 모든 코드(부하 시험, sample, 다른 서비스)
- violation: `"region": "jammy-a"`
- status: active
- source: jammy-collector README §3

### C-API-003 · endpoint
- rule: endpoint와 응답은 다음과 같다. 바꾸면 breaking change다.
  - `POST /api/v1/events`: 신규 201 `accepted`, 같은 `event_id`면 200 `duplicate`, 잘못된 `region` 400, DB 장애 503. 요청 필드는 `event_id`, `region`, `vehicle_id`, `speed_kmh`, `payload`.
  - `GET /api/v1/events/{event_id}`: 200, 없으면 404, DB 장애 503
  - `GET /api/v1/events`: 200 `{"items", "count"}`(`received_at DESC, event_id DESC`), `limit` 범위 초과 422
  - `GET /healthz`(liveness), `GET /ready`(readiness, DB 실패 503), `GET /metrics`(Prometheus)
- scope: jammy-collector `src/*`, collector를 호출하는 모든 코드
- violation: 중복 이벤트에 409 반환으로 변경
- status: active
- source: jammy-collector README §3

### C-API-004 · env
- rule: 필수 env는 `DATABASE_URL`(쓰기 원본)이다. 선택 env는 `DATABASE_READ_URL`, `SITE_ID`, `DEPLOY_ENV`(`dev`/`stage`/`prod`), `DB_POOL_MIN`, `DB_POOL_MAX`, `OTEL_SERVICE_NAME`(기본 `mobility-collector`), `OTEL_EXPORTER_OTLP_ENDPOINT`. env 이름 변경은 breaking change다. 승격 때는 코드를 바꾸지 않고 Secret의 `DATABASE_URL`·`DATABASE_READ_URL`만 바꿔야 한다(MUST).
- scope: jammy-collector, hybrid-5th `k8s/*`
- violation: env 이름 `DB_URL` 사용
- status: active
- source: jammy-collector README §2, §4

### C-API-005 · 로그의 payload
- rule: `payload` 원문을 로그에 남기면 안 된다(MUST NOT).
- scope: jammy-collector, collector 로그를 다루는 관측 설정
- violation: `logger.info(payload)`
- status: active
- source: jammy-collector README §5

### C-API-006 · HAProxy health 경로
- rule: HAProxy는 지금 app VM의 `GET /`(80)을 확인한다. 정할 것: Traefik이 컨테이너 8000으로 연결하는 경로, HAProxy가 `/healthz`와 `/ready` 중 무엇을 확인할지.
- status: open
- owner: YangJunMan, Hongsh6414
- source: Confluence 12943383, jammy-collector README §3

## DB

### C-DB-001 · 원본과 마이그레이션
- rule: 쓰기 원본은 A(10.11.x.130:5432)다. 마이그레이션(`python -m src.migrate`)은 쓰기 원본에만 실행해야 한다(MUST).
- scope: jammy-collector, hybrid-5th `k8s/*`(Job, initContainer)
- violation: 모든 거점 Pod 시작 시 마이그레이션 실행
- status: active
- source: jammy-collector README §4, Confluence 16973840

### C-DB-002 · 승격
- rule: 사본 승격은 기존 원본 격리와 쓰기 원본 1개 확인을 포함한 공동 절차로만 해야 한다(MUST). 자동 승격 코드를 단독으로 추가하면 안 된다(MUST NOT). 담당은 HYE0NWEST, jiwon28, daji0713이다.
- scope: 모든 repo
- violation: 장애 감지 시 B를 자동 승격하는 script
- status: active
- source: Confluence 12943361

### C-DB-003 · 복구 표현
- rule: 백업 복원 시험을 하지 않았다. 문서·대시보드·보고에서 "복구 검증 완료"라고 표현하면 안 된다(MUST NOT).
- scope: 모든 repo의 문서·대시보드
- violation: README에 "백업 복구 검증됨"
- status: active
- source: Confluence 12943361

### C-DB-004 · DB와 계정 이름
- rule: DB 이름(README 예시 `mobility`)과 앱 계정 이름(예시 `collector_writer`, `collector_reader`)을 확정해야 한다.
- status: open
- owner: HYE0NWEST

## 관측

### C-OBS-001 · label
- rule: metric label은 `site`(C-NAME-001 값), `layer`(`host`, `vm`, `k8s-node`, `pod`, `app`), `vantage`(관측 시점 거점, 거점 내부 수집은 `""`), `target_site`(블랙박스 대상 거점)를 쓴다(MUST).
- scope: jammy-observability, jammy-collector `/metrics`, hybrid-5th 관측 설정
- violation: label `host_site` 사용
- status: active
- source: jammy-observability README §2

### C-OBS-002 · 고유 ID label 금지
- rule: `event_id`, `vehicle_id`, `trace_id` 같은 고유 ID를 metric label에 넣으면 안 된다(MUST NOT). 고유 ID는 Loki 로그와 Tempo trace로만 추적한다.
- scope: metric을 만드는 모든 코드
- violation: `counter.labels(vehicle_id=...)`
- status: active
- source: jammy-observability README §2

### C-OBS-003 · 운영 데이터 필드
- rule: 분석·모델용 운영 로그와 지표는 `site`, `service`, `timestamp`, `run_id`, `request_id`, 단위를 식별할 수 있어야 한다(SHOULD). 실제 schema를 맞출 담당과 시점을 정해야 한다.
- status: open
- owner: YangJunMan, daji0713
- source: Confluence 12779522

## AWS

### C-AWS-001 · 필수 태그
- rule: 모든 AWS 리소스에 `Project=jammy`, `Part`, `Owner`, `ManagedBy`(Terraform `default_tags`)와 `Name`을 붙여야 한다(MUST).
- scope: hybrid-5th `infra/aws/*`
- violation: `default_tags` 없는 provider 추가
- status: active
- source: hybrid-5th `infra/aws/providers.tf`, Confluence 13139969

### C-AWS-002 · Component 태그
- rule: `Component` 값은 사용 중인 `edge`(입구), `network`(VPC·서브넷·IGW·라우팅), `ci`(GitHub Actions OIDC 역할)만 쓴다(MUST). 제안 단계 값(`mgmt`, `burst`, `storage`, `dns`)이나 새 값은 이 파일에 먼저 추가해야 한다(MUST).
- scope: hybrid-5th `infra/aws/*`
- violation: `Component = "web"`
- status: active
- source: Confluence 13139969, hybrid-5th `infra/aws/oidc.tf`

## AI 연동

### C-AI-001 · 모델 API 경계
- rule: 모델 API(`POST /predictions`, `GET /recommendations/{id}`, `/health/live`, `/health/ready`)는 로컬에서만 구현됐고 거점에 배포되지 않았다. 다른 파트 코드가 이 API를 운영 경로에서 호출하면 안 된다(MUST NOT). 모델이 준비되지 않으면 503을 반환하고, 예측값이나 Pod 수를 반환하지 않는다.
- scope: 모든 repo
- violation: HPA나 배포 script가 `/recommendations` 결과로 Pod 수를 바꿈
- status: active
- source: Confluence 12910594

### C-AI-002 · 운영 변경 권한
- rule: LLM이 Pod 수나 운영 설정을 정하면 안 된다(MUST NOT). 운영 변경은 사람이 판단한다. 분석 workflow는 오프라인 CLI이고 HTTP endpoint가 없다.
- scope: 모든 repo
- violation: LLM 출력으로 `kubectl scale` 실행
- status: active
- source: Confluence 12910594
