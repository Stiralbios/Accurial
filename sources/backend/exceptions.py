class CustomError(RuntimeError):
    def __init__(self, message, *args):
        # enforcing the use of a message
        self.message = message
        super().__init__(*args)


class CustomNotFoundError(CustomError):
    pass


class CustomNotAllowedError(CustomError):
    pass


class CustomAlreadyExistError(CustomError):
    pass


class InvariantViolation(RuntimeError):
    pass
