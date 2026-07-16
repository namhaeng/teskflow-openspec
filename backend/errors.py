from fastapi import HTTPException


class ApiError(HTTPException):
    """Standard error shape: { error: { code, message, ...meta } }"""

    def __init__(self, status_code: int, code: str, message: str, **meta):
        detail = {"error": {"code": code, "message": message, **({"meta": meta} if meta else {})}}
        super().__init__(status_code=status_code, detail=detail)


def validation_error(message="올바른 형식이 아닙니다"):
    return ApiError(400, "VALIDATION_ERROR", message)


def too_long(limit: int, actual: int):
    return ApiError(400, "TOO_LONG", f"{limit}자 이내로 입력하세요", limit=limit, actual=actual)


def invalid_credentials():
    return ApiError(401, "INVALID_CREDENTIALS", "이메일 또는 비밀번호가 일치하지 않습니다")


def token_expired():
    return ApiError(401, "TOKEN_EXPIRED", "인증이 만료되었습니다")


def forbidden(message="권한이 없습니다"):
    return ApiError(403, "FORBIDDEN", message)


def not_owner(message="본인의 메시지만 삭제할 수 있습니다"):
    return ApiError(403, "NOT_OWNER", message)


def not_found(message="해당 항목을 찾을 수 없습니다"):
    return ApiError(404, "NOT_FOUND", message)


def email_taken():
    return ApiError(409, "EMAIL_TAKEN", "이미 가입된 이메일입니다")


def already_in_team():
    return ApiError(409, "ALREADY_IN_TEAM", "이미 다른 팀에 소속되어 있습니다. 먼저 팀을 나가야 합니다")
