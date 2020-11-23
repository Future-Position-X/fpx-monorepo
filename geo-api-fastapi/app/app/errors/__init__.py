class UnauthorizedError(PermissionError):
    pass

class UserAlreadyExistsError(Exception):
    pass