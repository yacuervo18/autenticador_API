"""Interfaz de línea de comandos para diagnóstico y validación."""

from __future__ import annotations

import argparse
from pathlib import Path

from .inspector import inspection_json, inspect_storage, read_account_secret
from .profile import resolve_storage_dir
from .totp import TotpParameters, generate_totp


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cod-autenticador")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("--storage-dir", type=Path)
    inspect_parser.add_argument("--profile-dir", type=Path)
    inspect_parser.add_argument("--extension-id", default=None)
    inspect_parser.add_argument(
        "--storage-location",
        choices=("local", "sync"),
        default="local",
    )

    accounts_parser = subparsers.add_parser("accounts")
    accounts_parser.add_argument("--storage-dir", type=Path)
    accounts_parser.add_argument("--profile-dir", type=Path)
    accounts_parser.add_argument("--extension-id", default=None)
    accounts_parser.add_argument(
        "--storage-location", choices=("local", "sync"), default="local"
    )

    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--secret", required=True)
    generate_parser.add_argument("--algorithm", default="SHA1")
    generate_parser.add_argument("--digits", type=int, default=6)
    generate_parser.add_argument("--period", type=int, default=30)

    storage_generate_parser = subparsers.add_parser("generate-from-storage")
    storage_generate_parser.add_argument("--account", required=True)
    storage_generate_parser.add_argument("--storage-dir", type=Path)
    storage_generate_parser.add_argument("--profile-dir", type=Path)
    storage_generate_parser.add_argument("--extension-id", default=None)
    storage_generate_parser.add_argument(
        "--storage-location", choices=("local", "sync"), default="sync"
    )
    storage_generate_parser.add_argument("--algorithm", default="SHA1")
    storage_generate_parser.add_argument("--digits", type=int, default=6)
    storage_generate_parser.add_argument("--period", type=int, default=30)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command in {"inspect", "accounts", "generate-from-storage"}:
        kwargs = {
            "storage_dir": args.storage_dir,
            "profile_dir": args.profile_dir,
            "storage_location": args.storage_location,
        }
        if args.extension_id:
            kwargs["extension_id"] = args.extension_id
        path = resolve_storage_dir(**kwargs)
        if args.command == "inspect":
            print(inspection_json(inspect_storage(path)))
        elif args.command == "accounts":
            accounts = inspect_storage(path).accounts
            for account in accounts:
                print(
                    f"{account.account}\t{account.issuer}\t"
                    f"encrypted={account.encrypted}\t"
                    f"secret_available={account.secret_available}"
                )
        else:
            parameters = TotpParameters(
                algorithm=args.algorithm,
                digits=args.digits,
                period=args.period,
            )
            secret = read_account_secret(path, args.account)
            print(generate_totp(secret, parameters))
        return 0

    parameters = TotpParameters(
        algorithm=args.algorithm,
        digits=args.digits,
        period=args.period,
    )
    print(generate_totp(args.secret, parameters))
    return 0
