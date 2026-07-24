"""Hierarquia de exceções da aplicação AI CSV Query."""


class AppBaseError(Exception):
    """Exceção base da aplicação."""

    http_status: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str = "Ocorreu um erro interno na aplicação."):
        super().__init__(message)
        self.message = message


# Erros de Upload e Arquivo ZIP
class InvalidZipError(AppBaseError):
    http_status = 400
    code = "INVALID_ZIP"


class FileTooLargeError(AppBaseError):
    http_status = 413
    code = "FILE_TOO_LARGE"


class NoCSVFoundError(AppBaseError):
    http_status = 422
    code = "NO_CSV"


class NoDictionaryError(AppBaseError):
    http_status = 422
    code = "NO_DICTIONARY"


class InvalidCSVError(AppBaseError):
    http_status = 422
    code = "INVALID_CSV"


# Erros de Consulta e Dados
class DatasetNotFoundError(AppBaseError):
    http_status = 404
    code = "NOT_FOUND"


class SQLExecutionError(AppBaseError):
    http_status = 500
    code = "SQL_ERROR"


class LLMTimeoutError(AppBaseError):
    http_status = 504
    code = "LLM_TIMEOUT"


class UnsafeQueryError(AppBaseError):
    http_status = 400
    code = "UNSAFE_QUERY"
