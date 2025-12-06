
import subprocess
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_OAEP


def get_latest_commit_hash():
    """Get latest commit hash using Git."""
    out = subprocess.check_output(["git", "log", "-1", "--format=%H"])
    commit_hash = out.decode().strip()
    return commit_hash


def load_private_key(path):
    with open(path, "rb") as f:
        return RSA.import_key(f.read())


def load_public_key(path):
    with open(path, "rb") as f:
        return RSA.import_key(f.read())


def sign_message(commit_hash, private_key):
    """Sign commit hash using RSA-PSS + SHA256 (pycryptodome)."""
    msg_bytes = commit_hash.encode("utf-8")
    h = SHA256.new(msg_bytes)

    signer = pss.new(private_key)  # PSS with SHA256, salt_length=MAX by default
    signature = signer.sign(h)
    return signature


def encrypt_with_public_key(signature_bytes, public_key):
    """Encrypt with RSA-OAEP (SHA256)."""
    cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
    encrypted = cipher.encrypt(signature_bytes)
    return encrypted


def main():
    # 1. Get commit hash
    commit_hash = get_latest_commit_hash()

    # 2. Load student private key
    private_key = load_private_key("student_private.pem")

    # 3. Sign commit hash
    signature = sign_message(commit_hash, private_key)

    # 4. Load instructor public key
    instructor_key = load_public_key("instructor_public.pem")

    # 5. Encrypt signature with RSA-OAEP-SHA256
    encrypted_sig = encrypt_with_public_key(signature, instructor_key)

    # 6. Base64 encode (single line)
    b64_encoded = base64.b64encode(encrypted_sig).decode()

    print("Commit Hash:", commit_hash)
    print("Encrypted Signature (Base64):")
    print(b64_encoded)


if __name__ == "__main__":
    main()