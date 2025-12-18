import datetime
from typing import Literal, Any

import jwt
import bcrypt

from order_service.dto.auth import TokenDTO


class AuthHelper:
    def __init__(
        self,
        secret_key: str,
        hashing_algorithm: str,
        access_token_exp_minutes: int,
        refresh_token_exp_minutes: int,
    ) -> None:
        self._secret_key = secret_key
        self._hashing_algorithm = hashing_algorithm
        self._access_token_exp_minutes = access_token_exp_minutes
        self._refresh_token_exp_minutes = refresh_token_exp_minutes

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        return hashed_password.decode()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        raise NotImplementedError()

    def create_jwt_token(
        self, scope: Literal["access", "refresh"], user_id: str
    ) -> TokenDTO:
        payload = self._build_token_payload(scope, user_id)
        token = jwt.encode(payload, self._secret_key, algorithm=self._hashing_algorithm)

        return TokenDTO(
            raw_str=token,
            token_type=scope,
        )

    def _build_token_payload(
        self, scope: Literal["access", "refresh"], user_id: str
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "uid": user_id,
            "scope": scope,
        }

        if scope == "access":
            payload["exp"] = datetime.datetime.now() + datetime.timedelta(
                minutes=self._access_token_exp_minutes
            )
        elif scope == "refresh":
            payload["exp"] = datetime.datetime.now() + datetime.timedelta(
                minutes=self._refresh_token_exp_minutes
            )
        else:
            raise ValueError(f"Invalid scope type {scope}")

        return payload
