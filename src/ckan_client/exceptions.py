class CkanError(Exception):
    pass

class CkanActionError(CkanError):
    def __init__(self, error: dict, status_code: int):
        self.error = error
        self.status_code = status_code
        super().__init__(str(error))

class CkanValidationError(CkanActionError):
    def __init__(self, error: dict, status_code: int):
        self.field_errors = {k: v for k, v in error.items() if k not in ("__type__", "message")}
        super().__init__(error, status_code)