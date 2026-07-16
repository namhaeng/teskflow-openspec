## Why

MVP 초기 "1인 1팀" 원칙은 실제 사용 패턴(여러 프로젝트를 동시에 진행하는 사용자)을 반영하지 못했다. 사용자는 로그인 후에도 새 과제(프로젝트)를 자유롭게 추가/합류할 수 있어야 하고, 여러 과제를 오가며 작업할 수 있어야 한다. 아울러 프론트엔드는 수동 DOM 조작으로 유지보수가 어려워지고 있어 반응형 컴포넌트 패턴으로 정리가 필요했다.

## What Changes

- **다중 과제 소속**: `users.team_id` 단일 FK를 폐기하고 `team_memberships`(다대다) 테이블로 전환. 한 사용자가 여러 과제를 생성/소유하고 여러 과제에 동시에 멤버로 합류할 수 있음
- **과제 활성/비활성 상태**: owner가 과제를 활성/비활성 토글 가능. 비활성 과제는 조회만 가능하고 태스크/메시지 등 쓰기 작업은 차단
- **로그인 직행 플로우**: 로그인/가입 후 바로 칸반 화면으로 이동. 과제가 없으면 칸반 화면 자체에서 빈 상태를 보여주고 좌측 사이드바를 통해 생성/합류
- **UI 재구성**: 좌측에 "내 과제" 사이드바(전환·활성화 토글), 우측에 과제 멤버/초대코드 패널, 상단 네비게이션은 과제명만 표시하도록 단순화. 채팅은 별도 페이지 이동 대신 우측 200px 슬라이드 인/아웃 패널로 전환
- **초대코드 접근 제한**: 초대코드는 과제 owner에게만 상시 노출 (팀 멤버 패널). member는 "나가기" 액션만 노출
- **프론트엔드 아키텍처 전환**: Vanilla JS 수동 DOM 조작 방식에서 Vue 3(CDN) 컴포넌트 패턴으로 전환. 공유 컴포넌트(`TeamSidebar`, `TopNav`, `AddTeamModal`)로 반복 코드 제거
- **버그 수정**: 비활성 과제에서 쓰기 작업 실패 시 에러가 표시되지 않던 문제, 로그인 실패 시 일반 "UNAUTHORIZED" 메시지가 뜨던 문제, 모바일 햄버거 메뉴에 닫기 버튼이 없던 문제 수정

**BREAKING**: 기존 "1인 1팀" 가정 하의 `users.team_id` API 계약 제거. `standalone teams.html` 페이지 제거 (기능은 kanban.html에 통합)

## Capabilities

### New Capabilities
(신규 capability 없음 — 기존 capability의 요구사항 변경)

### Modified Capabilities
- `team`: 다중 소속(`team_memberships`), 과제 활성/비활성 상태, `GET /teams/mine`, owner 전용 `PATCH /teams/{id}/active`, owner 나가기 제한 추가
- `kanban-task`: 비활성 과제에서 태스크 쓰기 작업 차단 추가
- `chat`: 비활성 과제에서 메시지 전송 차단 추가

## Impact

- **DB**: `users.team_id` 컬럼 제거, `team_memberships` 테이블 추가, `teams.is_active` 컬럼 추가
- **API**: `GET /teams/mine`, `PATCH /teams/{id}/active` 신규. 기존 팀 관련 엔드포인트의 멤버십 검증 로직을 `team_memberships` 기준으로 전면 수정
- **프론트엔드**: `teams.html` 제거, `frontend/js/components.js`(Vue 컴포넌트) 신규, `kanban.html`/`chat.html`/`index.html`/`signup.html` 전면 재작성, `members.html` 제거(기능은 칸반 우측 패널로 이동)
- **비기능**: 기존 ACME Constraints/Metrics는 유지, "1인 1팀" 관련 Assumption은 폐기
