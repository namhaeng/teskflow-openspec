## 1. DB 스키마

- [x] 1.1 `users.team_id` 컬럼 제거
- [x] 1.2 `team_memberships`(team_id, user_id, role, unique) 테이블 추가
- [x] 1.3 `teams.is_active` 컬럼 추가 (기본값 true)

## 2. 백엔드 API

- [x] 2.1 `require_team_member`/`require_active_team_member` 의존성을 멤버십 테이블 기준으로 재작성
- [x] 2.2 `POST /teams` — 다중 소유 허용 (제한 제거)
- [x] 2.3 `GET /teams/mine` 신규 구현
- [x] 2.4 `POST /teams/join` — 다중 멤버십 허용, 중복 합류 409 처리
- [x] 2.5 `DELETE /teams/{id}/leave` — owner 나가기 차단(403), member만 허용
- [x] 2.6 `PATCH /teams/{id}/active` 신규 구현 (owner 전용)
- [x] 2.7 태스크/메시지 쓰기 라우트에 `require_active_team_member` 적용
- [x] 2.8 `GET /teams/{id}`, `GET /teams/{id}/members` 응답에 `role`/`is_active` 포함

## 3. 프론트엔드 — 로그인 플로우

- [x] 3.1 로그인/가입 후 `teams.html` 대신 `kanban.html`로 직행
- [x] 3.2 `kanban.html`이 `?team=` 없을 때 `GET /teams/mine` 조회 후 자동 리다이렉트 또는 빈 상태 렌더링
- [x] 3.3 `teams.html` 페이지 제거, 과제 생성/합류를 `AddTeamModal` 공용 컴포넌트로 통합

## 4. 프론트엔드 — Vue 3 전환 및 UI 재구성

- [x] 4.1 Vue 3 CDN 도입, `frontend/js/components.js`에 `TeamSidebar`/`TopNav`/`AddTeamModal` 공용 컴포넌트 작성
- [x] 4.2 `index.html`/`signup.html`/`kanban.html`/`chat.html`을 Vue `createApp()` 기반으로 재작성
- [x] 4.3 좌측 "내 과제" 사이드바: 과제 목록/전환/owner용 활성-비활성 토글
- [x] 4.4 우측 과제 멤버 패널: 멤버 목록 + owner 전용 초대코드 노출 + member용 "나가기" 버튼
- [x] 4.5 `members.html` 페이지 제거, 기능을 칸반 우측 패널로 통합
- [x] 4.6 상단 헤더에서 칸반/채팅 탭 제거, 현재 과제명만 bold로 표시
- [x] 4.7 채팅을 별도 페이지 이동 대신 200px 우측 슬라이드 인/아웃 패널로 전환
- [x] 4.8 로그인 화면과 통일된 그라데이션 비주얼을 회원가입/칸반 화면까지 확장
- [x] 4.9 칸반 보드 너비가 사이드바/우측 패널을 제외한 영역을 100% 채우도록 처리

## 5. 버그 수정

- [x] 5.1 비활성 과제에서 태스크 생성/수정/삭제/드래그 실패 시 에러 메시지 노출 (기존 무응답 실패 수정)
- [x] 5.2 로그인 실패(401) 시 일반 인터셉터가 가로채 "UNAUTHORIZED"를 표시하던 문제 수정 → 실제 서버 메시지 표시
- [x] 5.3 모바일 햄버거 메뉴에 닫기 버튼 추가

## 6. 검증

- [x] 6.1 다중 과제 생성/합류/전환 시나리오 브라우저 검증 (owner 2개 과제 + member 합류)
- [x] 6.2 과제 활성/비활성 토글 및 비활성 과제 쓰기 차단(403) 검증
- [x] 6.3 owner 나가기 차단, member 나가기 허용 검증
- [x] 6.4 초대코드 owner 전용 노출(비owner에게 미노출) 검증
- [x] 6.5 채팅 슬라이드 패널 열기/닫기/메시지 송수신/삭제 검증
- [x] 6.6 모바일 뷰포트(390x844) 반응형 검증
