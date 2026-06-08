import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


KEY_FILES = (
    "root_ca.key.pem",
    "intermediate_ca.key.pem",
    "signer.key.pem",
)


def main() -> None:
    target_dir = Path(sys.argv[1])
    password = sys.argv[2].encode("utf-8")
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in KEY_FILES:
        path = target_dir / filename
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        )
        path.write_bytes(pem)


if __name__ == "__main__":
    main()
