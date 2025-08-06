import os
import hvac
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./config/.env.vault.secrets")

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_ROOT_TOKEN = os.getenv("VAULT_DEV_ROOT_TOKEN_ID")


def import_totp():
    try:
        # Initialize Vault client
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        # Verify authentication
        if not client.is_authenticated():
            print("Error: Could not authenticate with Vault")
            return

        print(f"Connected to Vault at: {VAULT_ADDR}")

        # Enable TOTP engine if not enabled
        if 'totp/' not in client.sys.list_mounted_secrets_engines()['data']:
            client.sys.enable_secrets_engine(
                backend_type='totp',
                path='totp'
            )
            print("TOTP engine enabled at 'totp/'")

        # Import TOTP using BASE32 key
        totp_key = {
            'key': 'JBSWY3DPEHPK3PXP',  # Example BASE32 key
            'issuer': 'My Application',
            'account_name': 'user@example.com',
            'algorithm': 'SHA1',
            'period': 30,
            'digits': 6
        }

        # Create TOTP key
        client.write(
            path='totp/keys/my-app-imported',
            **totp_key
        )
        print("✅ TOTP successfully imported")

        # Generate TOTP code for verification
        totp_code = client.read('totp/code/my-app-imported')
        print(f"Generated TOTP code: {totp_code['data']['code']}")

        # Read TOTP configuration
        totp_config = client.read('totp/keys/my-app-imported')
        print("\nTOTP Configuration:")
        print(totp_config['data'])

    except hvac.exceptions.VaultError as e:
        print(f"Vault Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Function to validate a TOTP code
def validate_totp_code(code):
    try:
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        result = client.write(
            path='totp/code/my-app-imported',
            code=code
        )

        print(f"Valid code: {result['data']['valid']}")
        return result['data']['valid']

    except hvac.exceptions.VaultError as e:
        print(f"Vault Error: {e}")
        return False


# Function to import TOTP from URL
def import_totp_from_url():
    try:
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        # Import TOTP using URL
        totp_config = {
            'url': 'otpauth://totp/My%20Application:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=My%20Application&algorithm=SHA1&digits=6&period=30'
        }

        client.write(
            path='totp/keys/my-app-url',
            **totp_config
        )
        print("✅ TOTP successfully imported from URL")

    except hvac.exceptions.VaultError as e:
        print(f"Vault Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Import TOTP
    import_totp()

    # Example code validation
    test_code = input("Enter a TOTP code to validate: ")
    validate_totp_code(test_code)