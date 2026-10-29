import tempfile
import unittest
from pathlib import Path

from cod_autenticador.inspector import inspect_storage, read_account_secret
from cod_autenticador.profile import resolve_storage_dir
from cod_autenticador.service import MfaCodeService


class InspectorTests(unittest.TestCase):
    def test_inspection_is_read_only_and_reports_indicators(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory)
            (path / "CURRENT").write_text("MANIFEST-000001\n", encoding="ascii")
            (path / "LOCK").write_bytes(b"")
            (path / "000003").write_bytes(
                b'{"dataType":"OTPStorage","account":"test","issuer":"Example",'
                b'"encrypted":false,"secret":"JBSWY3DPEHPK3PXP","type":1}'
            )

            result = inspect_storage(path)

            self.assertTrue(result.has_lock)
            self.assertIn("CURRENT", result.leveldb_indicators)
            self.assertIn("JBSWY3DPEHPK3PXP", result.base32_candidates)
            self.assertEqual(result.accounts[0].account, "test")
            self.assertTrue(result.accounts[0].secret_available)
            self.assertEqual(read_account_secret(path, "test"), "JBSWY3DPEHPK3PXP")
            self.assertIn(b'"secret":"JBSWY3DPEHPK3PXP"', (path / "000003").read_bytes())

            service = MfaCodeService.from_storage(path, "test")
            self.assertEqual(len(service.get_code("test")), 6)

    def test_profile_resolves_sync_storage(self) -> None:
        result = resolve_storage_dir(
            profile_dir=Path(r"C:\Chrome\User Data\Default"),
            storage_location="sync",
        )
        self.assertEqual(
            result,
            Path(
                r"C:\Chrome\User Data\Default\Sync Extension Settings"
                r"\bhghoamapcdpbohphigoooaddinpkbai"
            ),
        )
