"""Deliberate pyca/cryptography calls used as CBOM scanner ground truth."""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


DATA = b"cbom-lab-fixture"


def aes_gcm() -> bytes:
    encryptor = Cipher(algorithms.AES(b"A" * 16), modes.GCM(b"I" * 12)).encryptor()
    return encryptor.update(DATA) + encryptor.finalize() + encryptor.tag


def aes_cbc() -> bytes:
    padded = DATA + b"\x10" * 16
    encryptor = Cipher(algorithms.AES(b"B" * 16), modes.CBC(b"V" * 16)).encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def rsa_oaep() -> bytes:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key.public_key().encrypt(
        DATA,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def sha256() -> bytes:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(DATA)
    return digest.finalize()


def md5() -> bytes:
    digest = hashes.Hash(hashes.MD5())  # Deliberately weak fixture.
    digest.update(DATA)
    return digest.finalize()


def pbkdf2() -> bytes:
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=b"S" * 16, iterations=120_000
    ).derive(b"test-only")


def ecdsa() -> bytes:
    private_key = ec.generate_private_key(ec.SECP256R1())
    return private_key.sign(DATA, ec.ECDSA(hashes.SHA256()))


def ecdh() -> bytes:
    alice = ec.generate_private_key(ec.SECP256R1())
    bob = ec.generate_private_key(ec.SECP256R1())
    return alice.exchange(ec.ECDH(), bob.public_key())


if __name__ == "__main__":
    outputs = [aes_gcm(), aes_cbc(), rsa_oaep(), sha256(), md5(), pbkdf2(), ecdsa(), ecdh()]
    assert all(outputs)
    print("python-fixture-ok", [len(output) for output in outputs])
