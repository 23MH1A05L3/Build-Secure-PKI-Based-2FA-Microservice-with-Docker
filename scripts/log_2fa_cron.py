#!/usr/bin/env python3
"""
Cron script to log current TOTP code every minute.
Writes a single line to stdout in the format:
YYYY-MM-DD HH:MM:SS - 2FA Code: {code}
Cron will append that stdout into /cron/last_code.txt (see crontab).
"""

import sys
from datetime import datetime
import os

# import your totp generator
try:
    from totp_utils import generate_totp_code
except Exception as exc:
    # If totp_utils missing or broken, write error to stdout/stderr for debugging
    print(f"ERROR: failed to import totp_utils: {exc}", file=sys.stderr)
    sys.exit(1)


SEED_PATH = "/data/seed.txt"

def main():
    # 1) Read seed (graceful if not present)
    if not os.path.exists(SEED_PATH):
        # Nothing to do if seed not present; write a short message (cron will capture it)
        print("Seed missing")
        return

    try:
        with open(SEED_PATH, "r") as f:
            hex_seed = f.read().strip()
    except Exception as exc:
        print(f"ERROR: cannot read seed: {exc}", file=sys.stderr)
        return

    if not hex_seed:
        print("Seed empty")
        return

    # 2) Generate TOTP code
    try:
        code = generate_totp_code(hex_seed)
    except Exception as exc:
        print(f"ERROR: TOTP generation failed: {exc}", file=sys.stderr)
        return

    # 3) UTC timestamp
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # 4) Output formatted line (stdout)
    print(f"{ts} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
