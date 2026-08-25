#!/usr/bin/env python3
"""Generate an explicitly expired, test-only X.509 certificate for the lab."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


ROOT = Path(__file__).resolve().parents[1]
CERTS = ROOT / "certs"
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
name = x509.Name(
    [
        x509.NameAttribute(NameOID.COMMON_NAME, "cbom-lab-expired"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CBOM Lab"),
    ]
)
now = datetime.now(timezone.utc)
certificate = (
    x509.CertificateBuilder()
    .subject_name(name)
    .issuer_name(name)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(now - timedelta(days=366))
    .not_valid_after(now - timedelta(days=1))
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    .sign(key, hashes.SHA256())
)

(CERTS / "expired-private-key.pem").write_bytes(
    key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
)
(CERTS / "expired-cert.pem").write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
(CERTS / "expired-private-key.pem").chmod(0o600)
print("generated test-only expired certificate")
