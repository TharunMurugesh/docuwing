class DocuwingError(Exception):
    status_code = 400
    code = "docuwing_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(DocuwingError):
    status_code, code = 404, "not_found"


class ValidationError(DocuwingError):
    status_code, code = 422, "validation_error"


class ProviderError(DocuwingError):
    status_code, code = 503, "provider_error"
