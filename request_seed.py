# Assuming you have the 'requests' library installed: pip install requests
import requests
import json
import os

def request_seed(student_id: str, github_repo_url: str, api_url: str):
    # 1. Read student public key from PEM file
    try:
        with open("student_public.pem", "r") as f:
            # Read all lines
            public_key_lines = f.readlines()
            # Join the lines into a single string with '\n' as the line break
            # This is the CRITICAL formatting step!
            public_key = "".join(public_key_lines)
            
    except FileNotFoundError:
        print("Error: student_public.pem not found. Did you complete Step 2?")
        return
    # 2. Prepare HTTP POST request payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    print(f"Sending request to API for student ID: {student_id}...")

    # 3. Send POST request to instructor API
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        return

    # 4. Parse JSON Response
    try:
        response_data = response.json()
        
        # Extract and handle errors first
        if response_data.get("error"):
            print(f"API Error: {response_data['error']}")
            return

        encrypted_seed = response_data.get("encrypted_seed")
        if not encrypted_seed:
            print("Error: 'encrypted_seed' field missing from successful response.")
            return

        print("Successfully received encrypted seed.")
        
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response.")
        print(f"Raw response: {response.text}")
        return

    # 5. Save encrypted seed to file
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)
        
    print(f"Encrypted seed saved to {os.path.abspath('encrypted_seed.txt')}")

# --- Execution ---
# REPLACE THESE PLACEHOLDERS with your actual details:
MY_STUDENT_ID = "23MH1A05L3" 
MY_GITHUB_REPO_URL = "https://github.com/23MH1A05L3/Build-Secure-PKI-Based-2FA-Microservice-with-Docker.git" 
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"

# Run the function
request_seed(MY_STUDENT_ID, MY_GITHUB_REPO_URL, API_URL)