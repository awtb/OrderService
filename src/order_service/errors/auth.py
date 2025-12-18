from order_service.errors.common import InvalidData, NotAllowedError


class UserAlreadyExistsError(InvalidData):
    message = "User already exists"


class IncorrectEmailOrPasswordError(NotAllowedError):
    message = "Incorrect email or password"
