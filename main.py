# main.py
import os
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict

from crypto_utils import load_private_key, decrypt_seed  # your file from Step5
from totp_utils import generate_totp_code, verify_totp_code  # your file from Step6

app = FastAPI(title="PKI 2FA Microservice")

PRIVATE_KEY_PATH = "student_private.pem"   # should be in repo
SEED_FILE_PATH = "/data/seed.txt"          # required by assignment
# For local dev you may also use "./data/seed.txt" but grader reads /data/seed.txt

# ---- Pydantic request models ----
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class Verify2FARequest(BaseModel):
    code: str


# ---- Helpers ----
def read_seed_file(path: str = SEED_FILE_PATH) -> str:
    """Read and return the hex seed from the configured seed file.
       Raises HTTPException(500) if file missing or invalid."""
    if not os.path.isfile(path):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    s = Path(path).read_text().strip()
    if len(s) != 64 or any(c not in "0123456789abcdef" for c in s):
        # guard against corrupt file
        raise HTTPException(status_code=500, detail="Invalid seed file")
    return s


# ---- Endpoint 1: POST /decrypt-seed ----
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: DecryptSeedRequest):
    # 1) Validate input present (pydantic does this)
    try:
        # Load student's private key
        private_key = load_private_key(PRIVATE_KEY_PATH)

        # Decrypt and validate (decrypt_seed returns 64-char hex or raises)
        hex_seed = decrypt_seed(payload.encrypted_seed, private_key)

        # Ensure directory exists (inside container /data)
        os.makedirs(os.path.dirname(SEED_FILE_PATH), exist_ok=True)

        # Write file with Unix LF, no extra text
        with open(SEED_FILE_PATH, "w", newline="\n") as f:
            f.write(hex_seed)

        # Protect file permissions (works in Linux / container)
        try:
            os.chmod(SEED_FILE_PATH, 0o600)
        except Exception:
            # on Windows this may do nothing; that's OK for development
            pass

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        # For security don't reveal internals, but return the expected 500 shape
        raise HTTPException(status_code=500, detail="Decryption failed")


# ---- Endpoint 2: GET /generate-2fa ----
@app.get("/generate-2fa")
def generate_2fa_endpoint():
    # Implementation checklist:
    # - Check if /data/seed.txt exists
    # - Read hex seed
    # - Generate TOTP, compute seconds left (valid_for)
    try:
        seed = read_seed_file(SEED_FILE_PATH)
    except HTTPException:
        raise

    # generate TOTP code (6 digits)
    try:
        code = generate_totp_code(seed)
    except Exception:
        raise HTTPException(status_code=500, detail="Error generating TOTP")

    # calculate seconds remaining in current 30-second period
    period = 30
    now = int(time.time())
    seconds_into_period = now % period
    valid_for = period - seconds_into_period
    # valid_for should be between 1..30 (0 means new period started - return 30)
    if valid_for == 0:
        valid_for = period

    return {"code": code, "valid_for": valid_for}


# ---- Endpoint 3: POST /verify-2fa ----
@app.post("/verify-2fa")
def verify_2fa_endpoint(payload: Verify2FARequest):
    # Validate request: payload.code must exist (pydantic ensures this)
    code = payload.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    # Read seed file
    try:
        seed = read_seed_file(SEED_FILE_PATH)
    except HTTPException:
        raise

    # Verify code, using valid_window=1 (previous/current/next)
    try:
        valid = verify_totp_code(seed, code, valid_window=1)
    except Exception:
        # if any internal error treat as 500
        raise HTTPException(status_code=500, detail="Error verifying code")

    return {"valid": bool(valid)}
