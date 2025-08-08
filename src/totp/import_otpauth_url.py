import os

import hvac
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../config/.env.vault.secrets")

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_ROOT_TOKEN = os.getenv("VAULT_DEV_ROOT_TOKEN_ID")


def import_totp_from_otpauth_url(otpauth_url, key_name):
    try:
        # Initialize Vault client
        client = hvac.Client(
            url=VAULT_ADDR,
            token=VAULT_ROOT_TOKEN
        )

        # Verify authentication
        if not client.is_authenticated():
            print("Error: Could not authenticate with Vault")
            return False

        print(f"Connected to Vault at: {VAULT_ADDR}")

        # Enable TOTP engine if not enabled
        if 'totp/' not in client.sys.list_mounted_secrets_engines()['data']:
            client.sys.enable_secrets_engine(
                backend_type='totp',
                path='totp'
            )
            print("TOTP engine enabled at 'totp/'")

        # Write TOTP configuration to Vault
        client.write_data(
            path=f'totp/keys/{key_name}',
            data={'url': otpauth_url}  # Changed to use write_data with data parameter
        )
        print(f"✅ TOTP successfully imported with key name: {key_name}")

        # Generate a test code
        totp_code = client.read(f'totp/code/{key_name}')
        print(f"Test code generated: {totp_code['data']['code']}")

        return True

    except hvac.exceptions.VaultError as e:
        print(f"Vault Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def read_totp_code(key_name):
    """Read the current TOTP code"""
    try:
        client = hvac.Client(
            url=VAULT_ADDR,
            token=VAULT_ROOT_TOKEN
        )

        if not client.is_authenticated():
            print("Error: Not authenticated with Vault")
            return None

        response = client.read(f'totp/code/{key_name}')
        if response and 'data' in response:
            return response['data']['code']
        return None

    except Exception as e:
        print(f"Error reading TOTP: {e}")
        return None


def main():
    # Load TOTP URL from .env.secrets
    load_dotenv("../config/.env.secrets")
    otpauth_url = os.getenv('OTPAUTH_URL')

    key_name = input("Enter a name for this TOTP key: ")

    if import_totp_from_otpauth_url(otpauth_url, key_name):
        print("\nReading current TOTP code...")
        code = read_totp_code(key_name)
        if code:
            print(f"Current TOTP code: {code}")
        else:
            print("Failed to read TOTP code")


if __name__ == "__main__":
    main()
