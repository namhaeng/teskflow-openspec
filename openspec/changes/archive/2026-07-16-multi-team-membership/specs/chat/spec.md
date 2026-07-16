## MODIFIED Requirements

### Requirement: 메시지 전송
시스템은 1000자 이내의 메시지 전송을 허용해야 하며(SHALL), 클라이언트와 서버 양쪽에서 길이를 검증해야 한다. 과제가 비활성 상태이면 전송을 차단해야 한다.

#### Scenario: 비활성 과제에서 전송 시도
- **WHEN** 비활성화된 과제에 멤버가 `POST /teams/{id}/messages`를 호출하면
- **THEN** 시스템은 403과 `{ error: { code: 'FORBIDDEN' } }`를 반환한다

#### Scenario: 정상 전송
- **WHEN** 팀 멤버가 1000자 이내 메시지로 `POST /teams/{id}/messages`를 호출하면
- **THEN** 시스템은 201과 함께 생성된 메시지(발신자, 시각 포함)를 반환한다

#### Scenario: 1000자 초과
- **WHEN** 1000자를 초과하는 메시지로 전송을 시도하면
- **THEN** 시스템은 400과 `{ error: { code: 'TOO_LONG', limit: 1000, actual: <length> } }`를 반환한다
