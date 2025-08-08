import dataclasses
import os
import time
from datetime import datetime
from typing import Optional

import hvac
from dotenv import load_dotenv


@dataclasses.dataclass
class TOTPCode:
    code: str
    remaining_seconds: int


class TOTPReader:
    def __init__(self):
        # Load environment variables
        load_dotenv("../config/.env.vault.secrets")

        self.vault_addr = os.getenv("VAULT_ADDR")
        self.vault_token = os.getenv("VAULT_DEV_ROOT_TOKEN_ID")
        self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)

    def get_current_totp_code(self, key_name) -> Optional[TOTPCode]:
        """
        Get the current TOTP code for a specific key
        """
        try:
            if not self.client.is_authenticated():
                print("Error: Not authenticated with Vault")
                return None

            # Read the current TOTP code
            response = self.client.read(f'totp/code/{key_name}')

            if response and 'data' in response:
                code = response['data']['code']
                # Calculate remaining time
                remaining_time = 30 - datetime.now().second % 30

                return TOTPCode(code=code, remaining_seconds=remaining_time)

            else:
                print(f"Error: Could not read TOTP for key '{key_name}'")
                return None

        except hvac.exceptions.VaultError as e:
            print(f"Vault Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def list_totp_keys(self):
        """
        List all available TOTP keys
        """
        try:
            response = self.client.list('totp/keys')
            if response and 'data' in response:
                return response['data']['keys']
            return []
        except Exception as e:
            print(f"Error listing TOTP keys: {e}")
            return []


def main():
    reader = TOTPReader()

    # List all available TOTP keys
    print("Available TOTP keys:")
    keys = reader.list_totp_keys()

    if not keys:
        print("No TOTP keys found in Vault")
        return

    for i, key in enumerate(keys, 1):
        print(f"{i}. {key}")

    # Let user select a key
    selected = input("\nEnter key name to read (or press Enter to read all): ").strip()

    if selected:
        # Read specific key
        result = reader.get_current_totp_code(selected)
        if result:
            print(f"\nTOTP for {selected}:")
            print(f"Code: {result.code}")
            print(f"Expires in: {result.remaining_seconds} seconds")

            if result.remaining_seconds <= 10:
                print("\nWARNING: TOTP code is about to expire in less than 10 seconds!")
                time.sleep(result.remaining_seconds + 1)
                print("Waiting remaining seconds for generate next code...")

                result = reader.get_current_totp_code(selected)
                print(f"\nTOTP for {selected}:")
                print(f"Code: {result.code}")
                print(f"Expires in: {result.remaining_seconds} seconds")
    else:
        # Read all keys
        print("\nCurrent TOTP codes:")
        for key in keys:
            result = reader.get_current_totp_code(key)
            if result:
                print(f"\n{key}:")
                print(f"Code: {result.code}")
                print(f"Expires in: {result.remaining_seconds} seconds")


if __name__ == "__main__":
    main()
