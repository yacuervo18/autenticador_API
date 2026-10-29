import unittest

from cod_autenticador.errors import ConfigurationError
from cod_autenticador.totp import TotpParameters, generate_totp


class TotpTests(unittest.TestCase):
    def test_rfc6238_sha1_vector(self) -> None:
        secret = "12345678901234567890"
        # RFC 6238 uses the ASCII secret encoded as Base32 for this interface.
        import base64

        encoded_secret = base64.b32encode(secret.encode()).decode()
        self.assertEqual(
            generate_totp(
                encoded_secret,
                TotpParameters(algorithm="SHA1", digits=8, period=30),
                timestamp=59,
            ),
            "94287082",
        )

    def test_sha256_vector(self) -> None:
        import base64

        encoded_secret = base64.b32encode(
            b"12345678901234567890123456789012"
        ).decode()
        self.assertEqual(
            generate_totp(
                encoded_secret,
                TotpParameters(algorithm="SHA256", digits=8, period=30),
                timestamp=59,
            ),
            "46119246",
        )

    def test_invalid_secret_is_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            generate_totp("not-a-valid-secret")
