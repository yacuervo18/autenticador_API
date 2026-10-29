"""Descubrimiento de perfiles Chrome en Windows."""

from __future__ import annotations

import os
from pathlib import Path

from .errors import ConfigurationError


EXTENSION_ID = "bhghoamapcdpbohphigoooaddinpkbai"


def default_chrome_user_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise ConfigurationError("No existe la variable de entorno LOCALAPPDATA.")
    return Path(local_app_data) / "Google" / "Chrome" / "User Data"


def resolve_storage_dir(
    *,
    storage_dir: Path | None = None,
    profile_dir: Path | None = None,
    extension_id: str = EXTENSION_ID,
    storage_location: str = "local",
) -> Path:
    """Resuelve el directorio de extensión sin crearlo ni modificarlo."""
    if storage_dir is not None and profile_dir is not None:
        raise ConfigurationError("Use storage_dir o profile_dir, no ambos.")
    if storage_dir is not None:
        return storage_dir
    if storage_location not in {"local", "sync"}:
        raise ConfigurationError(
            "storage_location debe ser 'local' o 'sync'."
        )
    selected_profile = profile_dir or (default_chrome_user_data_dir() / "Default")
    directory_name = (
        "Local Extension Settings"
        if storage_location == "local"
        else "Sync Extension Settings"
    )
    return selected_profile / directory_name / extension_id
