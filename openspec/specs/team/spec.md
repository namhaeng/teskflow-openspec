## Purpose

팀 생성/합류/탈퇴, 초대코드 관리, 팀 멤버십 기반 접근 제어를 담당한다. 1인 1팀 원칙을 따른다.

## Requirements

### Requirement: 팀 생성 및 초대코드 발급
시스템은 팀 생성 시 생성자를 owner로 지정하고, `대문자4-숫자4` 형식(`^[A-Z]{4}-[0-9]{4}$`)의 초대코드를 자동 생성해야 한다(SHALL). 사용자는 1인 1팀 원칙에 따라 동시에 하나의 팀에만 소속될 수 있다.

#### Scenario: 팀 생성
- **WHEN** 팀 미소속 사용자가 `POST /teams`에 팀 이름(1-30자)을 전달하면
- **THEN** 시스템은 201과 함께 `id`, `name`, `invite_code`, `owner_id`를 반환하고 `users.team_id`를 갱신한다

### Requirement: 초대코드 팀 미리보기
시스템은 실제 합류 전에 초대코드로 팀 이름, 멤버 수, owner 이메일을 미리 확인할 수 있는 조회 기능을 제공해야 한다(SHALL). 이 조회는 `users.team_id`를 변경하지 않는다.

#### Scenario: 유효한 코드 미리보기
- **WHEN** 사용자가 `GET /teams/preview?invite_code=`에 유효한 초대코드를 전달하면
- **THEN** 시스템은 200과 함께 `{ name, member_count, owner_email }`을 반환하고 팀 소속 상태는 변경하지 않는다

#### Scenario: 잘못된 코드 미리보기
- **WHEN** 형식이 올바르지 않거나 존재하지 않는 초대코드로 미리보기를 요청하면
- **THEN** 시스템은 각각 400 `VALIDATION_ERROR` 또는 404 `NOT_FOUND`를 반환한다

### Requirement: 초대코드로 팀 합류
시스템은 유효한 초대코드로 팀 합류 요청을 처리해야 한다(SHALL). 형식 오류, 미존재, 이미 다른 팀 소속인 경우를 구분해 에러를 반환해야 한다.

#### Scenario: 정상 합류
- **WHEN** 팀 미소속 사용자가 유효한 초대코드로 `POST /teams/join`을 호출하면
- **THEN** 시스템은 200과 함께 팀 정보를 반환하고 `users.team_id`를 해당 팀으로 갱신한다

#### Scenario: 초대코드 형식 오류
- **WHEN** `^[A-Z]{4}-[0-9]{4}$` 형식에 맞지 않는 코드로 합류를 시도하면
- **THEN** 시스템은 400과 `{ error: { code: 'VALIDATION_ERROR' } }`를 반환한다

#### Scenario: 초대코드 미존재
- **WHEN** 존재하지 않는 초대코드로 합류를 시도하면
- **THEN** 시스템은 404와 `{ error: { code: 'NOT_FOUND' } }`를 반환한다

#### Scenario: 이미 다른 팀 소속
- **WHEN** 이미 다른 팀에 소속된 사용자가 새 초대코드로 합류를 시도하면
- **THEN** 시스템은 409를 반환하며, 먼저 `DELETE /teams/{id}/leave`로 기존 팀을 나가야 새 팀에 합류할 수 있음을 안내한다

### Requirement: 팀 나가기
시스템은 팀 멤버가 스스로 팀을 떠날 수 있도록 해야 한다(SHALL). 나가면 `users.team_id`는 NULL이 되고, 이후 다른 팀에 재합류할 수 있다.

#### Scenario: 팀 나가기
- **WHEN** 팀 소속 사용자가 `DELETE /teams/{id}/leave`를 호출하면
- **THEN** 시스템은 200을 반환하고 `users.team_id`를 NULL로 갱신하며, 사용자는 팀 선택 화면으로 이동한다

#### Scenario: 나간 뒤 재합류
- **WHEN** 팀을 나간 사용자가 다른(또는 같은) 팀의 초대코드로 다시 합류를 시도하면
- **THEN** 시스템은 정상 합류 시나리오와 동일하게 200과 팀 정보를 반환한다

### Requirement: 팀 멤버 목록 조회
시스템은 팀 멤버 목록을 owner/member 구분과 함께 반환해야 한다(SHALL).

#### Scenario: 멤버 목록 조회
- **WHEN** 팀 멤버가 `GET /teams/{id}/members`를 호출하면
- **THEN** 시스템은 200과 함께 각 멤버의 이메일, 역할(owner/member), 합류일을 반환한다

### Requirement: 비멤버 접근 차단
시스템은 요청자가 해당 팀의 멤버가 아니면 모든 `/teams/{id}/*` 및 관련 리소스 요청을 403으로 차단해야 한다(SHALL).

#### Scenario: 비멤버의 다른 팀 접근
- **WHEN** team_id=1인 사용자가 `GET /teams/2/tasks`를 호출하면
- **THEN** 시스템은 403과 `{ error: { code: 'FORBIDDEN' } }`를 반환한다

### Requirement: 팀 정보 조회
시스템은 팀 ID로 팀 기본 정보를 조회할 수 있어야 한다(SHALL).

#### Scenario: 팀 정보 조회
- **WHEN** 팀 멤버가 `GET /teams/{id}`를 호출하면
- **THEN** 시스템은 200과 함께 팀 이름, 초대코드, owner_id, 생성일을 반환한다
