from crypto_utils import load_private_key, decrypt_seed

private_key = load_private_key("student_private.pem")

encrypted_seed = """
veDaIWAZzTP7cjFmxQmR0H8l/JSHwal+oiPzrovV4AYhuoh/eVX1YRzbXlNUAOz1mysC1w6HLwRHdd+55YVUQfSEIyuKEcg2r3FkK7BKrh59CITqoGv5usqPwoiVGyn8Zf+VrJg1fFFbMtLbXQKKN/ROkfeweYCt7voHSX6OZ8eMsPrb/TJXr/56CbTYF3KBtKAddW4bABri18Gk+jbFkDBcTdSYop5i8bDOkBsjdpej+KcFTl4a7vA+SDGg41fQZm0wwhyASiXoRS0uuSpBUBq/SaZtv7ds4uYr4ipW5lx/dAvcoUBtNc6s8whGvZhR67dsDc17MEoMmMozek15WYbc58qVXBJrV9BLz8NHMw6mYaI6xTTHTVgE8XKn1ImTHzGIJM0VC5RDjTiZRNcvy+bdlRsUnOtwj3Gdcv/UIbvtch3SjTXFE9UOAOtOel7WyYvDim+LDFJkB9xwxsyxqpsUI7JKST2kgRxmp6jTUHSDREcArCwfA6wSrnX7brmpuJvftKBrVTm+OU7/S4OWkSMubCjkIORycOpaRGkNk49cZDpfIK9kS7NwzH4ESOqmv4PoLEE76wwfUiQhYPcfRk80MMjJk92yJf4tRuXAyJjN1iVx3NjDJEqcmIGK1hv7aBWi+dJbfcdsIZpKifO3PrsxwkabtYxrFNAsHwZvkDo=
"""

encrypted_seed = encrypted_seed.strip()

try:
    seed = decrypt_seed(encrypted_seed, private_key)
    print("Decrypted seed:", seed)
except Exception as e:
    print("Error:", e)
