class BaseException(Exception):
    def __str__(self):
        return self.message


class InvalidFugueFormError(BaseException):
    def __init__(self, message: str):
        self.message = message
