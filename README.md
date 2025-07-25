# Hashicorp Vault

docker-compose up -d

# Verificar que Vault está en funcionamiento
docker compose exec -e VAULT_TOKEN=mi_token_root vault vault status

# Listar secretos
docker compose exec -e VAULT_TOKEN=mi_token_root vault vault kv list kv/

# Leer un secreto específico
docker compose exec -e VAULT_TOKEN=mi_token_root vault vault kv get kv/mi-app/desarrollo

# 1. **Obtener un valor específico** del secreto usando el formato
docker compose exec -e VAULT_TOKEN=mi_token_root vault vault kv get -field=db_usuario kv/mi-app/desarrollo

# 1. **Actualizar valores específicos** sin modificar los demás
docker compose exec -e VAULT_TOKEN=mi_token_root vault vault kv patch -mount=kv mi-app/desarrollo \
    api_key="nueva-api-key"
# 1. **Ver el historial de versiones** del secreto:
docker compose exec -e VAULT_TOKEN=mi_token_root vault vault kv metadata get -mount=kv mi-app/desarrollo


# Crear el secreto de desarrollo
docker compose exec -e VAULT_TOKEN=mi_token_root vault vault kv put -mount=kv mi-app/desarrollo \
    db_usuario="usuario_desarrollo" \
    db_password="password_desarrollo" \
    api_key="api-key-desarrollo"

# Crear el secreto de produccion
docker compose exec -e VAULT_TOKEN=mi_token_root vault vault kv put -mount=kv mi-app/produccion \
    db_usuario="usuario_produccion" \
    db_password="password_produccion" \
    api_key="api-key-produccion"

# Verificar la conexión a la API de Vault
docker compose exec vault curl \
    -H "X-Vault-Token: mi_token_root" \
    http://127.0.0.1:8200/v1/sys/health


# Detener los contenedores
docker compose down -v

# Iniciar de nuevo
docker compose up -d
