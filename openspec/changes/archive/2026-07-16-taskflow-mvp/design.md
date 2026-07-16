## Context

TaskFlow는 Day 2 MVP로, 프로그램정의 PDF(2장)와 스토리보드 PDF(42슬라이드, v2)에서 정의된 스펙을 그대로 구현한다. 두 문서 사이에 존재하던 API 구성 불일치, 동시접속자 수, 팀 탈퇴 정책은 propose 전 다음과 같이 확정했다:

- API 18개 구성은 스토리보드(A-03 결정 추적표, G-02)를 최종 기준으로 채택
- 동시 접속자: 팀당 5명 이내 (프로그램정의의 "동시 50명"은 오기로 판단, 미션의 "3-5인 팀"과 일치하는 스토리보드 값 채택)
- `DELETE /teams/{id}/leave`는 범위 내 기능으로 유지. 이에 따라 C-04의 "다른 팀 소속 시 합류 불가(범위 외)" 문구는 "떠난 뒤 재합류 가능"으로 정정

## Goals / Non-Goals

**Goals:**
- 인증, 팀, 칸반, 채팅, 배포 5개 기능을 API 18개 + DB 4테이블로 완전 구현
- 모든 에러 응답을 `{ error: { code, message } }` 표준으로 통일
- 팀 멤버십 기반 접근 제어(403)와 리소스 소유권 기반 삭제 권한을 미들웨어/의존성 레벨에서 일관 적용

**Non-Goals:**
- 알림(이메일/SMS/푸시), 파일 첨부, 전문 검색, 세분화된 페이지별 권한, 다국어, WebSocket 실시간, 자동화 테스트(pytest/jest) — 모두 Day 2 범위 외
- 팀 추방·역할 변경, 초대코드 재발급, JWT 갱신 토큰 — 범위 외

## Decisions

1. **DB**: SQLAlchemy 모델로 users/teams/tasks/messages 4테이블. `DATABASE_URL` 환경변수로 로컬 SQLite ↔ 운영 Neon(PostgreSQL) 전환. `users.team_id`(nullable, FK teams), `tasks.assignee_id`(nullable, FK users) 포함.
2. **인증**: JWT(24h 만료, 갱신 없음) + bcrypt 해시. 로그아웃은 stateless(블랙리스트 없음, 서버는 200만 반환, 클라이언트가 토큰 폐기).
3. **API 라우팅**: `PATCH /tasks/{id}/status`(상태 변경)와 `PUT /tasks/{id}`(제목 수정)를 분리. Task 삭제는 creator 또는 team owner만. Message 삭제는 본인만(owner도 예외 없음).
4. **팀 멤버십**: 1인 1팀 원칙(`users.team_id`). 팀을 나가면(`DELETE /teams/{id}/leave`) team_id가 NULL이 되어 팀 선택 화면으로 복귀, 이후 다른 팀에 재합류 가능.
5. **"내 태스크" 정의**: `tasks.assignee_id = current_user_id`(생성자 기준이 아님).
6. **채팅**: 5초 폴링, `since=` 파라미터로 증분 조회. 메시지 1000자 제한을 클라이언트+서버 양쪽에서 검증.
7. **프론트엔드**: Vanilla JS + Tailwind CSS, 프레임워크 없이 fetch API로 18개 엔드포인트 호출.
8. **배포**: 로컬은 FastAPI(uvicorn) + SQLite 파일 + 정적 파일 서빙. 운영은 Vercel(FE 정적 파일 + BE Serverless Functions) + Neon Postgres.

## Risks / Trade-offs

- [JWT 갱신 없음 → 24시간 후 강제 재로그인] → 범위 외로 명시, 사용자에게는 401 발생 시 자동 redirect로 마찰 최소화
- [로그아웃이 stateless라 탈취된 토큰을 강제 만료할 수 없음] → Day 2 범위에서는 수용, 향후 블랙리스트 도입 여지를 남겨둠
- [팀 나가기 기능과 기존 "다른 팀 소속 시 합류 불가" 문구가 충돌] → 이번 확정으로 "나간 뒤 재합류 가능"으로 정리, UI 에러 메시지도 동일하게 수정 필요
- [동시 접속자 5명/팀 이내 가정] → 이를 초과하는 트래픽 처리(커넥션 풀, 폴링 부하)는 설계 범위 밖

## Migration Plan

신규 프로젝트이므로 별도 마이그레이션 불필요. 최초 배포 시 Neon에 스키마 생성(Alembic 또는 SQLAlchemy `create_all`) 후 Vercel에 연결.

## Open Questions

없음 (Critical 결정 #1-4는 propose 전 확정, Optional 결정 #5-8은 위 Decisions에 반영 완료)
