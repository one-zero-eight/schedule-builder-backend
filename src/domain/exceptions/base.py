class AppException(Exception):
    status_code: int = 500
    detail: str = "server error"
