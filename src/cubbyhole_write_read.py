import os

import hvac
from dotenv import load_dotenv

load_dotenv("./config/.env.vault.secrets")

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_ROOT_TOKEN = os.getenv("VAULT_DEV_ROOT_TOKEN_ID")

# Secret to store
SECRET_PATH = "cubbyhole/my_personal_secret"
SECRET_DATA = {
    "username": "example_user",
    "password": "my_secure_password_123!"
}


def store_secret_in_cubbyhole():
    """
    Store a secret in the HashiCorp Vault cubbyhole.
    """
    try:
        # Initialize the HVAC client
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        # Verify if the client is authenticated
        if not client.is_authenticated():
            print("Error: Could not authenticate with Vault. Please verify token and URL.")
            return

        print(f"Connected to Vault at: {VAULT_ADDR}")

        write_response = client.write(SECRET_PATH, **SECRET_DATA)

        print(f"Secret successfully stored at: {SECRET_PATH}")
        print("Vault write response:", write_response)

    except hvac.exceptions.VaultError as e:
        print(f"Vault Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def read_secret_from_cubbyhole():
    """
    Read a secret stored in the HashiCorp Vault cubbyhole.
    """
    try:
        # Initialize the HVAC client
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        # Verify if the client is authenticated
        if not client.is_authenticated():
            print("Error: Could not authenticate with Vault. Please verify token and URL.")
            return None

        print(f"Connected to Vault at: {VAULT_ADDR}")

        # Read the secret from cubbyhole
        # For cubbyhole, use the 'read' method directly
        read_response = client.read(SECRET_PATH)

        if read_response is None:
            print(f"No secret found at path: {SECRET_PATH}")
            return None

        # Secret data is in the 'data' key of the response
        read_secret = read_response['data']
        print(f"Secret successfully read from: {SECRET_PATH}")
        print("Secret data:")
        for key, value in read_secret.items():
            # For password, you might want to hide its real value in the output
            if key == "password":
                print(f"  {key}: {'*' * len(value)}")  # Show asterisks instead of actual password
            else:
                print(f"  {key}: {value}")

        return read_secret

    except hvac.exceptions.VaultError as e:
        print(f"Vault Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    store_secret_in_cubbyhole()

    secret = read_secret_from_cubbyhole()

    if secret:
        print("\nThe secret has been retrieved and can be used in your application.")
        # Example of how you could use the data:
        # username = secret.get('username')
        # password = secret.get('password')
        # print(f"Retrieved username: {username}")
        # print(f"Retrieved password: {password}") # Be careful when printing passwords!