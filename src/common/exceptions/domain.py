class ConflictError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnprocessableDomainError(Exception):
    """Domain validation failure mapped to HTTP 422 (Nest UNPROCESSABLE_ENTITY)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
