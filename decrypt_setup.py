import base64
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

# --- Function to load the Private Key ---
# Adjust the file_path if your private key is copied elsewhere in the container
def load_private_key(file_path: str = "student_private.pem"):
    """Loads the RSA private key from the PEM file."""
    try:
        with open(file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None # Key was generated without a password (NoEncryption)
            )
        return private_key
    except FileNotFoundError:
        print(f"ERROR: Private key file not found at {file_path}. Ensure it is present.")
        raise
    except Exception as e:
        print(f"ERROR: Failed to load private key: {e}")
        raise

# --- Step 5 Implementation Function ---
def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypts a Base64-encoded ciphertext using RSA/OAEP with SHA-256.
    
    Args:
        encrypted_seed_b64: Base64-encoded ciphertext string.
        private_key: The loaded RSA private key object.
        
    Returns:
        The decrypted 64-character hexadecimal seed string.
    """
    # 1. Base64 decode the encrypted seed string
    try:
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError(f"Base64 decoding failed: {e}")

    # 2. RSA/OAEP Decrypt with SHA-256 (CRITICAL PARAMETERS)
    oaep_padding = padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()), # MGF: MGF1 with SHA-256
        algorithm=hashes.SHA256(),                   # Hash: SHA-256
        label=None                                   # Label: None
    )

    try:
        # Perform the decryption
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            oaep_padding
        )
    except Exception as e:
        # Decryption failure often means incorrect padding/hash or a wrong private key
        raise Exception(f"RSA/OAEP Decryption failed. Check key, padding parameters, or ciphertext: {e}")
    
    # 3. Decode bytes to UTF-8 string
    decrypted_hex_string = decrypted_bytes.decode('utf-8')

    # 4. Validate: must be 64-character hex string
    if len(decrypted_hex_string) != 64:
        raise ValueError(f"Decrypted seed length is incorrect: {len(decrypted_hex_string)}. Expected 64.")
    
    if not all(c in '0123456789abcdef' for c in decrypted_hex_string.lower()):
        raise ValueError("Decrypted seed contains non-hexadecimal characters.")
    
    return decrypted_hex_string

# --- Execution Logic to Run the Decryption Setup ---
if __name__ == "__main__":
    ENCRYPTED_SEED_PATH = "encrypted_seed.txt"
    PRIVATE_KEY_PATH = "student_private.pem"
    # Project requirement: The decrypted seed MUST be saved here for persistence
    DECRYPTED_SEED_STORAGE_PATH = "/data/seed.txt" 
    
    print("--- Starting Seed Decryption Setup (Step 5) ---")

    try:
        # Load the encrypted seed from the file created in Step 4
        with open(ENCRYPTED_SEED_PATH, "r") as f:
            b64_ciphertext = f.read().strip()

        # Load your private key
        rsa_private_key = load_private_key(PRIVATE_KEY_PATH)

        # Decrypt the seed
        plaintext_seed = decrypt_seed(b64_ciphertext, rsa_private_key)
        
        print(f"Decryption successful. Decrypted seed length: {len(plaintext_seed)} characters.")
        
        # Create the necessary directory for the persistent volume
        os.makedirs(os.path.dirname(DECRYPTED_SEED_STORAGE_PATH), exist_ok=True)
        
        # Store the decrypted seed persistently for the microservice
        with open(DECRYPTED_SEED_STORAGE_PATH, "w") as f:
             f.write(plaintext_seed)
             
        print(f"Decrypted seed securely saved to: {DECRYPTED_SEED_STORAGE_PATH}")
        print("Setup complete. The microservice can now read the secret seed.")
        
    except Exception as e:
        print(f"\nFATAL SETUP ERROR: {e}")
        # Exit with a non-zero code to indicate setup failure
        exit(1)