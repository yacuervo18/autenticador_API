from pathlib import Path

from cod_autenticador import MfaCodeService


service = MfaCodeService.from_storage(
    storage_path=Path(
        r"C:\Users\yedicuja\AppData\Local\Google\Chrome\User Data"
        r"\Default\Sync Extension Settings"
        r"\bhghoamapcdpbohphigoooaddinpkbai"
    ),
    account_id="YEDICUJA",
)

codigo_mfa = service.get_code("YEDICUJA")

print(codigo_mfa)
