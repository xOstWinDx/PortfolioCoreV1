from dataclasses import dataclass


@dataclass
class Payload:
    sub: str
    expiration: int
    device_id: str
    token: str


@dataclass
class AuthMetaData:
    key: str  # f"tokens:{user_id}:{credentials_id}:{device_id}"
    payload: Payload
