class AppException(Exception):
    status_code: int
    detail: str
