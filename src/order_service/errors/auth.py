from order_service.errors.common import InvalidData
from order_service.errors.common import NotAllowedError


class UserAlreadyExistsError(InvalidData):
    message = "User already exists"


class IncorrectEmailOrPasswordError(NotAllowedError):
    message = "Incorrect email or password"
