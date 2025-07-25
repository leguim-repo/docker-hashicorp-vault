import os
import warnings

import hvac
from dotenv import load_dotenv

# Suppress deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv("./config/.env.vault.secrets")

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_ROOT_TOKEN = os.getenv("VAULT_DEV_ROOT_TOKEN_ID")

MY_APP_NAME = "my-app"
ENVIRONMENTS = ["dev", "pre", "prod"]


def read_secret(path):
    """Helper function to safely read secrets"""
    try:
        # Create Vault client
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        secret = client.secrets.kv.v2.read_secret_version(
            mount_point='kv',
            path=path,
            raise_on_deleted_version=True
        )
        return secret['data']['data']
    except hvac.exceptions.InvalidPath:
        print(f"Secret not found at path: {path}")
        return None
    except Exception as e:
        print(f"Error reading secret {path}: {str(e)}")
        return None


if __name__ == '__main__':

    for env in ENVIRONMENTS:
        print(f"Reading secrets for {env} environment...")
        secret = read_secret(f"{MY_APP_NAME}/{env}")
        if not secret:
            print(f"No secrets found for {env} environment.")

        print(f"Environment: {env}")
        for key, value in secret.items():
            if "password" in key:
                print(f"  {key}: {'*' * len(value)}")  # Show asterisks instead of actual password
            else:
                print(f"  {key}: {value}")
        print("-"*40)