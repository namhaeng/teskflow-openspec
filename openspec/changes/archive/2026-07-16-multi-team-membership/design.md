## Context

이 변경은 이미 로컬에서 구현·검증된 상태에서 사후적으로 문서화하는 change다. Day 2 MVP(`taskflow-mvp`) 아카이브 이후 사용자 피드백을 받아 "1인 1팀" 제약을 다중 소속 모델로 확장했고, 동시에 프론트엔드를 Vanilla JS에서 Vue 3(CDN) 컴포넌트 패턴으로 전환했다.

## Goals / Non-Goals

**Goals:**
- 사용자가 여러 과제를 동시에 생성/소속할 수 있게 한다
- owner가 과제를 비활성화해 읽기 전용으로 보관할 수 있게 한다
- 반복되는 화면 요소(사이드바, 상단바, 과제 추가 모달)를 재사용 가능한 Vue 컴포넌트로 정리한다
- 채팅 접근을 페이지 이동 없이 칸반 화면 내 슬라이드 패널로 단순화한다

**Non-Goals:**
- 팀 추방, 역할(role) 세분화, 초대코드 재발급 — 여전히 범위 외
- 빌드 도구 도입(Webpack/Vite) — Vue는 CDN 전역 빌드로 계속 사용, SFC/번들러 없음
- 실시간(WebSocket) 채팅 — 5초 폴링 유지

## Decisions

1. **`team_memberships` 다대다 테이블**: `users.team_id` 단일 FK 대신 별도 조인 테이블(`team_id`, `user_id`, `role`, unique(`user_id`,`team_id`))을 도입해 다중 소속을 표현. `teams.owner_id`는 유지하되 멤버십 role로도 owner를 표시해 조회를 단순화.
2. **`teams.is_active` 플래그 + `require_active_team_member` 의존성**: 읽기 전용 의존성(`require_team_member`)과 쓰기 전용 의존성(`require_active_team_member`)을 분리해 태스크/메시지 생성·수정·삭제 라우트에서만 활성 상태를 검사.
3. **owner는 탈퇴 불가, 비활성화만 가능**: 소유자가 사라지는 과제 상태를 방지하기 위한 단순한 제약. 소유권 이전은 범위 외로 남김.
4. **로그인 후 랜딩을 kanban.html로 통일**: `teams.html`을 별도 랜딩 페이지로 두지 않고, `kanban.html`이 `?team=` 파라미터 유무·`GET /teams/mine` 결과에 따라 자체적으로 빈 상태/자동 리다이렉트/보드를 렌더링. 과제 생성·합류는 `AddTeamModal` 공용 컴포넌트로 어디서든 호출 가능.
5. **Vue 3 CDN 전역 빌드 채택**: 별도 빌드 파이프라인 없이 `<script src="unpkg.../vue.global.prod.js">`로 도입. Options API로 각 페이지가 독립된 `createApp()` 루트를 가지며, `TeamSidebar`/`TopNav`/`AddTeamModal`을 전역 컴포넌트로 등록해 페이지 간 공유.
6. **채팅을 200px 슬라이드 드로어로 전환**: 별도 페이지 대신 칸반 화면 내부 상태(`chatOpen`)로 열고 닫는 `fixed` 패널을 구현. `translate-x-full`/`translate-x-0` + `transition-transform`으로 애니메이션. 폴링은 열려 있을 때만 데이터 갱신하도록 가드.
7. **초대코드 노출 범위**: `GET /teams/{id}` 응답의 `role` 필드로 프론트에서 owner 여부를 판별해 초대코드 UI를 조건부 렌더링. 서버 측에서도 별도로 강제하지는 않음(신뢰 경계는 "팀 멤버만 조회 가능"까지이며, 초대코드 자체는 owner/member 모두 API 응답에는 포함되지만 UI 상에서만 owner에게 노출).

## Risks / Trade-offs

- [팀 나가기 시 owner가 없어지는 문제] → owner는 나가기 자체를 차단, 비활성화로 대체
- [멤버십 테이블 조인 증가로 조회 쿼리 복잡도 상승] → 현재 규모(팀당 5명 내외)에서는 성능 영향 미미, 인덱스(`user_id`,`team_id`)로 커버
- [Vue CDN 전역 빌드는 번들 최적화/트리쉐이킹이 없음] → MVP 규모에서는 무시할 수준, 추후 실 서비스 확장 시 빌드 도구 도입 검토 필요
- [초대코드가 API 응답 자체에는 포함되어 있어 완전한 서버측 차단은 아님] → 현재는 UI 레벨 숨김만 보장. 강한 보안이 필요하면 서버에서 role 기반으로 필드 자체를 마스킹하는 후속 작업 필요

## Migration Plan

로컬 SQLite/개발 환경 기준으로 `Base.metadata.create_all()`이 스키마를 재생성하므로 별도 마이그레이션 스크립트 없이 반영됨. 운영(Neon) 배포 시에는 기존 `users.team_id` 컬럼 제거 및 `team_memberships` 테이블 생성을 위한 Alembic 마이그레이션이 필요(아직 미작성, 배포 단계에서 진행 예정).

## Open Questions

없음
