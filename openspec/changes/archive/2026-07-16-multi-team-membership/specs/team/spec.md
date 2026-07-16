## MODIFIED Requirements

### Requirement: 과제 생성 및 초대코드 발급
시스템은 로그인한 사용자가 언제든 새 과제를 생성할 수 있도록 해야 한다(SHALL). 생성 시 생성자를 owner로 지정하고, `대문자4-숫자4` 형식(`^[A-Z]{4}-[0-9]{4}$`)의 초대코드를 자동 생성한다. 사용자는 여러 과제를 동시에 생성/소유할 수 있다.

#### Scenario: 과제 생성
- **WHEN** 로그인한 사용자가 `POST /teams`에 과제 이름(1-30자)을 전달하면
- **THEN** 시스템은 201과 함께 `id`, `name`, `invite_code`, `owner_id`, `is_active`, `role: "owner"`를 반환하고 해당 사용자의 owner 멤버십을 생성한다

#### Scenario: 동일 사용자의 복수 과제 생성
- **WHEN** 이미 다른 과제를 소유한 사용자가 `POST /teams`로 또 다른 과제를 생성하면
- **THEN** 시스템은 제한 없이 201을 반환하고 새 과제의 owner 멤버십을 추가한다

### Requirement: 내 과제 목록 조회
시스템은 로그인한 사용자가 소속된 모든 과제(owner/member 무관)를 조회할 수 있어야 한다(SHALL).

#### Scenario: 내 과제 목록
- **WHEN** 사용자가 `GET /teams/mine`을 호출하면
- **THEN** 시스템은 200과 함께 사용자가 속한 모든 과제 목록을(각 항목에 `role` 포함) 생성일 순으로 반환한다

### Requirement: 초대코드로 과제 합류 (다중 소속)
시스템은 유효한 초대코드로 과제 합류 요청을 처리해야 한다(SHALL). 사용자는 여러 과제에 동시에 멤버로 소속될 수 있다. 형식 오류, 미존재, 이미 해당 과제의 멤버인 경우를 구분해 에러를 반환해야 한다.

#### Scenario: 정상 합류
- **WHEN** 사용자가 유효한 초대코드로 `POST /teams/join`을 호출하면
- **THEN** 시스템은 200과 함께 과제 정보를 반환하고 해당 사용자의 member 멤버십을 추가한다

#### Scenario: 다른 과제에 이미 소속된 상태에서 합류
- **WHEN** 이미 다른 과제의 멤버인 사용자가 새로운 과제의 초대코드로 합류를 시도하면
- **THEN** 시스템은 정상적으로 200을 반환하고 두 과제 모두에 대한 멤버십을 유지한다

#### Scenario: 초대코드 형식 오류
- **WHEN** `^[A-Z]{4}-[0-9]{4}$` 형식에 맞지 않는 코드로 합류를 시도하면
- **THEN** 시스템은 400과 `{ error: { code: 'VALIDATION_ERROR' } }`를 반환한다

#### Scenario: 초대코드 미존재
- **WHEN** 존재하지 않는 초대코드로 합류를 시도하면
- **THEN** 시스템은 404와 `{ error: { code: 'NOT_FOUND' } }`를 반환한다

#### Scenario: 동일 과제 중복 합류
- **WHEN** 이미 멤버인 과제의 초대코드로 다시 합류를 시도하면
- **THEN** 시스템은 409와 `{ error: { code: 'ALREADY_IN_TEAM' } }`를 반환한다

### Requirement: 과제 나가기 (owner 제외)
시스템은 member 역할의 사용자가 스스로 과제를 떠날 수 있도록 해야 한다(SHALL). owner는 과제를 나갈 수 없으며, 대신 비활성화해야 한다.

#### Scenario: 멤버의 나가기
- **WHEN** member 역할 사용자가 `DELETE /teams/{id}/leave`를 호출하면
- **THEN** 시스템은 200을 반환하고 해당 사용자의 멤버십을 삭제한다

#### Scenario: owner의 나가기 시도
- **WHEN** owner 역할 사용자가 자신이 owner인 과제에 대해 `DELETE /teams/{id}/leave`를 호출하면
- **THEN** 시스템은 403과 `{ error: { code: 'FORBIDDEN' } }`를 반환하며 비활성화를 안내한다

### Requirement: 과제 활성/비활성 상태 (owner 전용)
시스템은 과제 owner가 과제의 활성 상태를 토글할 수 있도록 해야 한다(SHALL). 비활성화된 과제는 조회는 가능하나 태스크/메시지 생성·수정·삭제 등 쓰기 작업은 차단된다.

#### Scenario: owner의 비활성화
- **WHEN** owner가 `PATCH /teams/{id}/active`에 `{ is_active: false }`를 전달하면
- **THEN** 시스템은 200과 함께 갱신된 과제 정보를 반환하고 이후 해당 과제에 대한 쓰기 요청을 403으로 차단한다

#### Scenario: 비활성 과제에서 쓰기 시도
- **WHEN** 비활성화된 과제에 대해 멤버가 태스크 생성/수정/삭제 또는 메시지 전송을 시도하면
- **THEN** 시스템은 403과 `{ error: { code: 'FORBIDDEN' } }`를 반환한다

#### Scenario: member의 활성 상태 변경 시도
- **WHEN** owner가 아닌 멤버가 `PATCH /teams/{id}/active`를 호출하면
- **THEN** 시스템은 403을 반환한다

### Requirement: 과제 정보 조회
시스템은 과제 ID로 과제 기본 정보(요청자의 역할 포함)를 조회할 수 있어야 한다(SHALL).

#### Scenario: 과제 정보 조회
- **WHEN** 과제 멤버가 `GET /teams/{id}`를 호출하면
- **THEN** 시스템은 200과 함께 과제 이름, 초대코드, owner_id, is_active, 요청자의 role을 반환한다
