## 1. 프로젝트 셋업

- [x] 1.1 FastAPI 프로젝트 구조 생성 (backend), Vanilla JS + Tailwind 프론트 구조 생성 (frontend)
- [x] 1.2 SQLAlchemy 모델 정의: users, teams, tasks, messages (design.md 스키마 기준)
- [x] 1.3 `DATABASE_URL` 환경변수 기반 SQLite/Neon 전환 설정
- [x] 1.4 로컬 개발 서버 실행 확인 (TestClient로 전체 플로우 스모크 테스트 통과)

## 2. 인증 (auth)

- [x] 2.1 bcrypt 비밀번호 해시 유틸 구현
- [x] 2.2 `POST /auth/signup` 구현 (이메일 형식 검증, 8자 이상 비밀번호, 중복 이메일 409)
- [x] 2.3 JWT 발급/검증 유틸 구현 (24h 만료)
- [x] 2.4 `POST /auth/login` 구현 (INVALID_CREDENTIALS 통일 메시지)
- [x] 2.5 `POST /auth/logout` 구현 (stateless, 200만 반환)
- [x] 2.6 `GET /auth/me` 구현
- [x] 2.7 JWT 인증 의존성(dependency)/미들웨어 구현 (401 TOKEN_EXPIRED 처리)
- [x] 2.8 프론트: 회원가입/로그인 화면, localStorage 토큰 관리, 401 인터셉터 → /login redirect

## 3. 팀 (team)

- [x] 3.1 초대코드 생성 로직 구현 (`^[A-Z]{4}-[0-9]{4}$`)
- [x] 3.2 `POST /teams` 구현 (owner 지정, users.team_id 갱신)
- [x] 3.3 `POST /teams/join` 구현 (형식 400 / 미존재 404 / 이미 소속 409)
- [x] 3.4 `DELETE /teams/{id}/leave` 구현 (team_id NULL 처리, 재합류 허용)
- [x] 3.5 `GET /teams/{id}`, `GET /teams/{id}/members` 구현
- [x] 3.6 팀 멤버십 검증 의존성 구현 (비멤버 403 FORBIDDEN)
- [x] 3.7 프론트: 팀 선택 화면(생성/합류), 팀 미소속 강제 redirect, 멤버 목록 사이드 패널 (members.html)
- [x] 3.8 `GET /teams/preview?invite_code=` 구현 + 프론트 초대코드 입력 시 팀명/멤버수/owner 미리보기 (team_id 변경 없음)

## 4. 칸반 태스크 (kanban-task)

- [x] 4.1 태스크 CRUD 라우트 구현: `GET/POST /teams/{id}/tasks`, `GET /tasks/{id}`
- [x] 4.2 `PATCH /tasks/{id}/status`, `PUT /tasks/{id}` 분리 구현
- [x] 4.3 `DELETE /tasks/{id}` 권한 검증 구현 (creator 또는 owner만, 그 외 403)
- [x] 4.4 필터 쿼리 구현: 전체 / `@me`(assignee_id=current_user) / 미할당
- [x] 4.5 프론트: 3컬럼 칸반 보드, 인라인 카드 생성, HTML5 드래그앤드롭 → PATCH 호출
- [x] 4.6 프론트: 카드 상세/수정 모달, 삭제 확인 다이얼로그
- [x] 4.7 프론트: empty state (컬럼별 카드 없음 화면)

## 5. 채팅 (chat)

- [x] 5.1 `GET /teams/{id}/messages?since=` 구현 (증분 조회)
- [x] 5.2 `POST /teams/{id}/messages` 구현 (1000자 서버 검증, TOO_LONG 400)
- [x] 5.3 `DELETE /messages/{id}` 구현 (본인만, NOT_OWNER 403)
- [x] 5.4 프론트: 채팅 화면, 5초 폴링(setInterval + since=), 1000자 클라이언트 카운터
- [x] 5.5 프론트: empty state, 본인 메시지 호버 삭제 메뉴

## 6. 에러 응답 표준화

- [x] 6.1 공통 에러 핸들러 구현: 모든 4xx/5xx를 `{ error: { code, message } }` 형태로 통일
- [x] 6.2 에러 코드 정의: VALIDATION_ERROR, TOO_LONG, INVALID_CREDENTIALS, TOKEN_EXPIRED, FORBIDDEN, NOT_OWNER, NOT_FOUND, EMAIL_TAKEN

## 7. 반응형/모바일 대응

- [x] 7.1 Tailwind breakpoint 적용 (<768px 모바일, 768-1024px 태블릿, >1024px 데스크탑) — md: 접두사로 nav/board 반응형 처리
- [x] 7.2 모바일 칸반 컬럼 탭 전환 + 카드 길게 누르기(터치) 상태 변경 프롬프트 (스와이프는 탭 전환으로 대체 구현)
- [x] 7.3 모바일 햄버거 메뉴 (풀스크린 오버레이). 채팅은 반응형 레이아웃만 적용, 별도 풀스크린/키보드 대응은 생략

## 8. 배포 (deployment)

- [ ] 8.1 Vercel 프로젝트 연결, `vercel.json`/Serverless Functions 설정
- [ ] 8.2 Neon Postgres 프로비저닝, `DATABASE_URL` 환경변수 설정
- [ ] 8.3 `main` push 시 자동 배포 확인
- [ ] 8.4 배포 후 5개 기능(인증/팀/칸반/채팅) 수동 동작 확인

## 9. 검증

- [x] 9.1 사용 시나리오 3종 수동 확인 (리더 흐름 / 신규 합류자 흐름 / 모바일 뷰포트 반응형 — 실제 배포 전 로컬 브라우저로 확인, 실기기 PC-모바일 교차 확인은 미실시)
- [x] 9.2 ACME Metrics 정성 확인: 신규 합류자 시나리오, 칸반 드래그+상태변경, 메시지 누락 0건(폴링 재동기화) 확인
- [x] 9.3 권한 격리 확인: 비멤버 403, 본인 아닌 태스크/메시지 삭제 시도 403(FORBIDDEN/NOT_OWNER)
- [x] 9.4 (추가) 전체 API 18개 + preview 엔드포인트 실사용 검증, 에러 응답 UI 표시(이메일 중복/형식, 비밀번호 8자, 로그인 실패, 초대코드 400/404, 메시지 1000자 초과), 잘못된 토큰 → 로그인 redirect, 모바일 햄버거 메뉴/컬럼 탭 전환 확인
  - 🐛 발견/수정: 로그인 실패(401) 시 `api.js` 전역 인터셉터가 서버 메시지 대신 "UNAUTHORIZED"를 표시하던 버그 → `/auth/login`, `/auth/signup`은 인터셉터 예외 처리로 수정
  - 🐛 발견/수정: 모바일 햄버거 메뉴에 닫기 버튼이 없어 오버레이가 뒤 화면을 막던 버그 → `×` 닫기 버튼 추가
