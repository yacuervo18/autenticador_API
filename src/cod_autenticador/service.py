"""Servicio desacoplado para solicitar códigos MFA."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from .errors import ConfigurationError
from .inspector import read_account_secret
from .totp import TotpParameters, generate_totp


class MfaCodeService:
    """Fachada estable para proveedores de secreto ya validados."""

    def __init__(
        self,
        accounts: Mapping[str, tuple[str, TotpParameters]] | None = None,
    ) -> None:
        self._accounts = dict(accounts or {})

    @classmethod
    def from_storage(
        cls,
        storage_path: Path,
        account_id: str,
        parameters: TotpParameters | None = None,
    ) -> "MfaCodeService":
        secret = read_account_secret(storage_path, account_id)
        return cls(
            {
                account_id: (
                    secret,
                    parameters or TotpParameters(),
                )
            }
        )

    def get_code(self, account_id: str) -> str:
        try:
            secret, parameters = self._accounts[account_id]
        except KeyError as exc:
            raise ConfigurationError(
                f"No existe una cuenta configurada: {account_id}"
            ) from exc
        return generate_totp(secret, parameters)
