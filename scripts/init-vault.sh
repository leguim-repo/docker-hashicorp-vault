#!/bin/sh

# Esperar a que Vault esté disponible
until vault status > /dev/null 2>&1; do
    echo "Esperando a que Vault esté disponible..."
    sleep 1
done

# Habilitar el motor de secretos KV version 2
vault secrets enable -version=2 kv

# Crear una política que permita leer y escribir en la ruta kv/mi-app
cat > /tmp/app-policy.hcl << EOF
path "kv/data/my-app/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
path "kv/metadata/my-app/*" {
  capabilities = ["list"]
}
EOF

# Crear la política en Vault
vault policy write app-policy /tmp/app-policy.hcl

# Leer el archivo de configuración
CONFIG_FILE="/config/vault.json"

if [ -f "$CONFIG_FILE" ]; then
    echo "Cargando secretos desde $CONFIG_FILE"

    # Procesar cada ruta de secretos en el archivo JSON
    for path in $(jq -r '.secrets | keys[]' $CONFIG_FILE); do
        # Obtener los secretos para esta ruta como una cadena JSON
        secrets=$(jq -r --arg path "$path" '.secrets[$path]' $CONFIG_FILE)

        # Crear el secreto en Vault
        echo $secrets | vault kv put kv/$path -

        echo "Secretos creados en: kv/$path"
    done

    echo "Inicialización completada"
else
    echo "Archivo de configuración no encontrado: $CONFIG_FILE"
    exit 1
fi