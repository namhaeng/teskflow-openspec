## ADDED Requirements

### Requirement: 회원가입
시스템은 이메일과 비밀번호(8자 이상)로 신규 계정을 생성해야 한다(SHALL). 비밀번호는 bcrypt로 해시하여 저장해야 하며, 평문으로 저장해서는 안 된다. 이메일 형식은 클라이언트와 서버 양쪽에서 검증한다.

#### Scenario: 정상 가입
- **WHEN** 사용자가 유효한 이메일과 8자 이상 비밀번호로 `POST /auth/signup`을 호출하면
- **THEN** 시스템은 201과 함께 JWT 및 사용자 정보(`id`, `email`, `team_id: null`)를 반환한다

#### Scenario: 이메일 형식 오류
- **WHEN** 이메일 형식이 올바르지 않은 값으로 가입을 시도하면
- **THEN** 시스템은 400과 `{ error: { code: 'VALIDATION_ERROR' } }`를 반환한다

#### Scenario: 이메일 중복
- **WHEN** 이미 가입된 이메일로 가입을 시도하면
- **THEN** 시스템은 409와 `{ error: { code: 'EMAIL_TAKEN' } }`를 반환한다

#### Scenario: 비밀번호 8자 미만
- **WHEN** 8자 미만의 비밀번호로 가입을 시도하면
- **THEN** 시스템은 400과 `{ error: { code: 'VALIDATION_ERROR' } }`를 반환한다

### Requirement: 로그인
시스템은 이메일/비밀번호 검증에 성공하면 24시간 만료의 JWT를 발급해야 한다(SHALL). 실패 시 이메일 존재 여부를 노출하지 않는 단일 에러 메시지를 반환해야 한다.

#### Scenario: 정상 로그인
- **WHEN** 등록된 이메일과 올바른 비밀번호로 `POST /auth/login`을 호출하면
- **THEN** 시스템은 200과 함께 24시간 만료 JWT, `user.team_id`를 반환한다

#### Scenario: 자격 증명 오류
- **WHEN** 이메일 또는 비밀번호가 일치하지 않으면
- **THEN** 시스템은 401과 `{ error: { code: 'INVALID_CREDENTIALS' } }`를 반환하며, 이메일 존재 여부는 응답에 드러나지 않는다

### Requirement: 로그아웃 (stateless)
시스템은 JWT 블랙리스트를 유지하지 않는다(SHALL NOT). `POST /auth/logout` 호출 시 200만 반환하며, 토큰 폐기는 클라이언트 책임이다.

#### Scenario: 로그아웃 호출
- **WHEN** 인증된 사용자가 `POST /auth/logout`을 호출하면
- **THEN** 시스템은 200과 빈 본문을 반환하고 서버 측 상태는 변경하지 않는다

### Requirement: JWT 만료 처리
시스템은 만료되었거나 누락된 JWT로 보호된 엔드포인트에 접근 시 401을 반환해야 한다(SHALL).

#### Scenario: 만료된 토큰으로 API 호출
- **WHEN** 24시간이 지난 JWT로 보호된 API를 호출하면
- **THEN** 시스템은 401과 `{ error: { code: 'TOKEN_EXPIRED' } }`를 반환한다

### Requirement: 현재 사용자 조회
시스템은 유효한 JWT로 `GET /auth/me` 호출 시 현재 로그인한 사용자 정보를 반환해야 한다(SHALL).

#### Scenario: 내 정보 조회
- **WHEN** 유효한 JWT로 `GET /auth/me`를 호출하면
- **THEN** 시스템은 200과 함께 `{ id, email, team_id }`를 반환한다
