"""Generación TOTP conforme a RFC 6238, sin dependencias externas."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Callable

from .errors import ConfigurationError


_HASHES = {
    "SHA1": hashlib.sha1,
    "SHA256": hashlib.sha256,
    "SHA512": hashlib.sha512,
}


@dataclass(frozen=True)
class TotpParameters:
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30

    def __post_init__(self) -> None:
        algorithm = self.algorithm.upper()
        if algorithm not in _HASHES:
            raise ConfigurationError(f"Algoritmo TOTP no soportado: {self.algorithm}")
        if self.digits not in (6, 8):
            raise ConfigurationError("TOTP debe usar 6 u 8 dígitos.")
        if self.period <= 0:
            raise ConfigurationError("El período TOTP debe ser positivo.")
        object.__setattr__(self, "algorithm", algorithm)


def _decode_secret(secret: str) -> bytes:
    normalized = "".join(secret.split()).upper()
    if not normalized:
        raise ConfigurationError("El secreto TOTP no puede estar vacío.")
    try:
        padding = "=" * (-len(normalized) % 8)
        return base64.b32decode(normalized + padding, casefold=True)
    except (binascii.Error, ValueError) as exc:
        raise ConfigurationError("El secreto no es Base32 válido.") from exc


def generate_totp(
    secret: str,
    parameters: TotpParameters | None = None,
    *,
    timestamp: float | None = None,
    clock: Callable[[], float] = time.time,
) -> str:
    """Genera un código TOTP para un instante determinado."""
    settings = parameters or TotpParameters()
    key = _decode_secret(secret)
    now = clock() if timestamp is None else timestamp
    counter = int(now // settings.period)
    counter_bytes = counter.to_bytes(8, byteorder="big", signed=False)
    digest = hmac.new(
        key,
        counter_bytes,
        _HASHES[settings.algorithm],
    ).digest()
    offset = digest[-1] & 0x0F
    binary_code = (
        ((digest[offset] & 0x7F) << 24)
        | ((digest[offset + 1] & 0xFF) << 16)
        | ((digest[offset + 2] & 0xFF) << 8)
        | (digest[offset + 3] & 0xFF)
    )
    return str(binary_code % (10**settings.digits)).zfill(settings.digits)
