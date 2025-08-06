
#!/bin/sh
# docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault sh /vault/scripts/test-totp.sh

# Create a test TOTP key
vault write totp/keys/test-app \
    generate=true \
    issuer="Test App" \
    account_name="test@example.com"

# Generate a TOTP code
vault read totp/code/test-app

echo "Configuración de TOTP verificada"