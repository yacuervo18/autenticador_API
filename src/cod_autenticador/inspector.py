"""Diagnóstico conservador del directorio LevelDB de la extensión."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .errors import ConfigurationError, StorageNotFoundError, UnsupportedStorageError


_PRINTABLE_RUN = re.compile(rb"[\x20-\x7e]{8,}")
_BASE32_CANDIDATE = re.compile(
    r"(?<![A-Z2-7])[A-Z2-7]{16,64}={0,6}(?![A-Z2-7])"
)
_EXPECTED_FILES = {"CURRENT", "LOCK", "LOG", "LOG.old", "MANIFEST-000001"}


@dataclass(frozen=True)
class StorageInspection:
    path: str
    exists: bool
    files: tuple[str, ...]
    has_lock: bool
    leveldb_indicators: tuple[str, ...]
    printable_candidates: tuple[str, ...]
    base32_candidates: tuple[str, ...]
    accounts: tuple["StorageAccount", ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class StorageAccount:
    account: str
    issuer: str
    encrypted: bool
    secret_available: bool
    data_type: str
    otp_type: int | None


def _read_files(path: Path) -> list[bytes]:
    contents: list[bytes] = []
    for file_path in path.iterdir():
        if file_path.is_file():
            try:
                contents.append(file_path.read_bytes())
            except OSError:
                continue
    return contents


def _find_storage_records(contents: list[bytes]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for content in contents:
        for match in re.finditer(rb"\{[^{}\r\n]{1,8192}\}", content):
            try:
                value = json.loads(match.group().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(value, dict) and value.get("dataType") == "OTPStorage":
                records.append(value)
    return records


def inspect_storage(path: Path) -> StorageInspection:
    if not path.exists() or not path.is_dir():
        raise StorageNotFoundError(f"No existe el directorio de almacenamiento: {path}")

    files = tuple(sorted(item.name for item in path.iterdir() if item.is_file()))
    indicators = tuple(sorted(set(files).intersection(_EXPECTED_FILES)))
    printable: set[str] = set()
    base32: set[str] = set()

    contents = _read_files(path)
    for content in contents:
        for match in _PRINTABLE_RUN.findall(content):
            value = match.decode("ascii", errors="ignore")
            printable.add(value)
            normalized = value.upper()
            base32.update(_BASE32_CANDIDATE.findall(normalized))

    accounts = tuple(
        StorageAccount(
            account=str(record.get("account", "")),
            issuer=str(record.get("issuer", "")),
            encrypted=bool(record.get("encrypted", False)),
            secret_available=isinstance(record.get("secret"), str),
            data_type=str(record.get("dataType", "")),
            otp_type=(
                int(record["type"])
                if isinstance(record.get("type"), int)
                else None
            ),
        )
        for record in _find_storage_records(contents)
    )

    return StorageInspection(
        path=str(path),
        exists=True,
        files=files,
        has_lock=(path / "LOCK").exists(),
        leveldb_indicators=indicators,
        printable_candidates=tuple(sorted(printable)),
        base32_candidates=tuple(sorted(base32)),
        accounts=accounts,
    )


def inspection_json(inspection: StorageInspection) -> str:
    return json.dumps(inspection.to_dict(), indent=2, ensure_ascii=False)


def read_account_secret(path: Path, account: str) -> str:
    """Lee un secreto únicamente de un registro OTPStorage no cifrado."""
    records = _find_storage_records(_read_files(path))
    matches = [record for record in records if record.get("account") == account]
    if not matches:
        raise ConfigurationError(f"No existe la cuenta en el almacenamiento: {account}")
    if len(matches) > 1:
        raise ConfigurationError(f"La cuenta no es única en el almacenamiento: {account}")
    record = matches[0]
    if record.get("encrypted") is True or not isinstance(record.get("secret"), str):
        raise UnsupportedStorageError(
            f"La cuenta '{account}' no tiene un secreto legible sin descifrado."
        )
    return record["secret"]
