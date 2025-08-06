import os

import hvac
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./config/.env.vault.secrets")

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_ROOT_TOKEN = os.getenv("VAULT_DEV_ROOT_TOKEN_ID")


def create_secrets():
    try:
        # Initialize Vault client
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        # Verify authentication
        if not client.is_authenticated():
            print("Error: Could not authenticate with Vault")
            return

        print(f"Connected to Vault at: {VAULT_ADDR}")

        # Enable KV version 2 secrets engine if not enabled
        if 'kv/' not in client.sys.list_mounted_secrets_engines()['data']:
            client.sys.enable_secrets_engine(
                backend_type='kv',
                path='kv',
                options={'version': 2}
            )
            print("KV v2 engine enabled at path 'kv/'")

        # Example secrets for different environments
        development_secrets = {
            'data': {
                'db_host': 'db-dev.example.com',
                'db_user': 'dev_user',
                'db_password': 'dev_password_123',
                'api_key': 'dev-api-key-123'
            }
        }

        production_secrets = {
            'data': {
                'db_host': 'db-prod.example.com',
                'db_user': 'prod_user',
                'db_password': 'prod_password_456',
                'api_key': 'prod-api-key-456'
            }
        }

        # Create development secrets
        client.secrets.kv.v2.create_or_update_secret(
            path='my-awesome-app/development',
            secret=development_secrets
        )
        print("✅ Development secrets created at 'kv/my-awesome-app/development'")

        # Create production secrets
        client.secrets.kv.v2.create_or_update_secret(
            path='my-awesome-app/production',
            secret=production_secrets
        )
        print("✅ Production secrets created at 'kv/my-awesome-app/production'")


    except hvac.exceptions.VaultError as e:
        print(f"Vault Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def read_secrets():
    try:
        # Initialize Vault client
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        # Verify authentication
        if not client.is_authenticated():
            print("Error: Could not authenticate with Vault")
            return

        print(f"Connected to Vault at: {VAULT_ADDR}")

        # Verify that secrets were created successfully
        dev_secrets = client.secrets.kv.v2.read_secret_version(
            mount_point='kv',
            path='my-awesome-app/development',
            raise_on_deleted_version=False
        )
        print("\nDevelopment secrets:", dev_secrets['data']['data'])

        prod_secrets = client.secrets.kv.v2.read_secret_version(
            mount_point='kv',
            path='my-awesome-app/production',
            raise_on_deleted_version=False
        )
        print("\nProduction secrets:", prod_secrets['data']['data'])

    except hvac.exceptions.VaultError as e:
        print(f"Vault Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    create_secrets()
    read_secrets()
