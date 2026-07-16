## Why

소규모 팀(3-5인)이 칸반 보드와 실시간(폴링 기반) 채팅을 한 화면에서 오가며 업무 진행 상황을 추적할 수 있는 도구가 없다. Day 2 MVP로 인증·팀·칸반·채팅·배포 5개 기능을 완전 정의된 스펙(ACME: Assumptions/Constraints/Metrics/Examples)에 따라 한 번에 구현하여, 구현 단계에서 AI가 임의로 가정하거나 범위를 벗어나지 않도록 한다.

## What Changes

- 이메일/비밀번호 회원가입·로그인, JWT(24h, 갱신 없음, stateless 로그아웃) 인증 도입
- 팀 생성/초대코드 발급/합류/멤버 목록 조회, **팀 나가기(`DELETE /teams/{id}/leave`)** 기능 포함 (1인 1팀 원칙 유지, 나간 뒤 재합류 가능하도록 범위 내로 확정)
- 칸반 보드: TODO/DOING/DONE 3컬럼, 카드 생성/드래그로 상태 변경(`PATCH /tasks/{id}/status`)/제목·담당자 수정/삭제, `assignee_id`(nullable) 기반 "내 태스크" 필터
- 팀 단위 채팅: 메시지 송수신(1000자 제한), 5초 폴링(`since=`), 본인 메시지만 삭제
- Vercel(FE+BE) + Vercel Storage Neon 배포, 로컬은 SQLite 단일 서버

**BREAKING**: 없음 (신규 프로젝트)

## Capabilities

### New Capabilities
- `auth`: 회원가입, 로그인, JWT 발급/검증, 로그아웃(stateless), bcrypt 비밀번호 해시
- `team`: 팀 생성, 초대코드 발급/합류, 멤버 목록, 팀 나가기, 멤버십 기반 접근 제어(403)
- `kanban-task`: TODO/DOING/DONE 태스크 CRUD, 상태 변경, 담당자 배정(nullable), 권한 기반 삭제(creator/owner)
- `chat`: 팀 단위 메시지 송수신, 5초 폴링 조회, 1000자 제한, 본인 메시지 삭제
- `deployment`: 로컬(SQLite/StaticFiles) ↔ 운영(Vercel + Neon) 환경 분리, `DATABASE_URL` 전환

### Modified Capabilities
(신규 프로젝트이므로 없음)

## Impact

- **DB**: users(+team_id), teams, tasks(+assignee_id, +created_at 인덱스), messages 4테이블 (SQLite 로컬 / PostgreSQL-Neon 운영)
- **API**: 총 18개 — Auth 4 + Team 5(create/join/get/members/leave) + Task 6(list/create/get/update-title/update-status/delete) + Chat 3(list-since/create/delete)
- **기술 스택**: Backend FastAPI, Frontend Vanilla JS + Tailwind CSS, 배포 Vercel Serverless Functions
- **비기능**: API 응답 100ms, 칸반 드래그 반응 50ms(정성 검증), 메시지 누락 0건, 에러 응답 `{ error: { code, message } }` 표준, 동시 접속자 팀당 5명 이내
- **범위 외**: 알림, 파일 첨부, 전문 검색, 세분화된 권한, 다국어, WebSocket, 자동화 테스트
