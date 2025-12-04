# test_totp.py
from totp_utils import generate_totp_code, verify_totp_code

# Replace with your real 64-char hex seed (do not commit this file)
hex_seed = "7a83d910424c58e2ff8c6ad09c739cedb3ef9dfe12ab7c8125a0c23bd8e29d4c"

print("Seed length:", len(hex_seed))
print("Is hex 64:", all(c in "0123456789abcdef" for c in hex_seed))

# Generate current TOTP
code = generate_totp_code(hex_seed)
print("Current TOTP:", code)

# Verify immediately (should be True)
valid = verify_totp_code(hex_seed, code, valid_window=1)
print("Verify returned:", valid)
