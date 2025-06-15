class AppException(Exception):
    status_code: int
    detail: str

    def __init__(self, status_code=500, detail="server error") -> None:
        self.status_code = status_code
        self.detail = detail
