import requests
import argparse
import urllib3
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Disable the InsecureRequestWarning when --no-ssl is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fuzz_api(no_ssl):
    # Step 1: Enter API endpoint with FUZZHERE placeholder
    endpoint = input("Enter the API endpoint with 'FUZZHERE' as the fuzzing point: ")

    if "FUZZHERE" not in endpoint:
        print("Error: The endpoint must contain 'FUZZHERE' to indicate where to fuzz.")
        return

    # Step 2: Provide JWT token and authorization format
    jwt_token = input("Enter your JWT token: ")

    # Ask the user whether to include "Bearer" or not
    auth_format = input("Do you want to use 'Bearer' before the token? (yes/no): ").strip().lower()
    
    if auth_format == 'yes':
        authorization_header = f"Bearer {jwt_token}"
    else:
        authorization_header = jwt_token

    # Step 3: Ask for the file with valid endpoints
    fuzz_file = input("Enter the path to the file with fuzzing inputs: ")

    try:
        # Open the file and read fuzz inputs
        with open(fuzz_file, 'r') as f:
            fuzz_inputs = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{fuzz_file}' not found.")
        return
    
    # Step 4: Set up headers for the request
    headers = {
        'Authorization': authorization_header,
        'Content-Type': 'application/json'
    }

    # Prepare a list to store successful fuzzing endpoints
    valid_endpoints = []

    # Step 5: Trigger API request and check responses
    for fuzz_input in fuzz_inputs:
        fuzz_input = fuzz_input.strip()  # Remove any extra spaces or newlines
        fuzzed_endpoint = endpoint.replace("FUZZHERE", fuzz_input)
        
        try:
            # Send the request, with or without SSL verification based on --no-ssl option
            # Disable redirects to capture 3xx status codes
            response = requests.get(fuzzed_endpoint, headers=headers, verify=not no_ssl, allow_redirects=False)

            # Output based on status codes with color formatting
            if response.status_code == 200:
                print(Fore.GREEN + f"Valid endpoint found: {fuzzed_endpoint} -> 200 OK")
                valid_endpoints.append(fuzzed_endpoint)
            elif 300 <= response.status_code < 400:
                print(Fore.BLUE + f"Fuzzed endpoint: {fuzzed_endpoint} -> Redirection (Status Code: {response.status_code})")
            elif 400 <= response.status_code < 500:
                print(Fore.YELLOW + f"Fuzzed endpoint: {fuzzed_endpoint} -> 400 Error (Status Code: {response.status_code})")
            elif 500 <= response.status_code < 600:
                print(Fore.RED + f"Fuzzed endpoint: {fuzzed_endpoint} -> 500 Server Error (Status Code: {response.status_code})")
            else:
                print(Fore.WHITE + f"Fuzzed endpoint: {fuzzed_endpoint} -> Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"Error with endpoint {fuzzed_endpoint}: {e}")

    # Output all valid endpoints
    if valid_endpoints:
        print(Fore.GREEN + "\nEndpoints with 200 OK response:")
        for valid in valid_endpoints:
            print(valid)
    else:
        print("\nNo valid endpoints found.")

if __name__ == "__main__":
    # Step 6: Argument parsing to handle --no-ssl option
    parser = argparse.ArgumentParser(description='Fuzz an API with JWT authentication and optional SSL verification bypass.')
    parser.add_argument('--no-ssl', action='store_true', help='Disable SSL certificate verification')
    args = parser.parse_args()

    fuzz_api(args.no_ssl)
