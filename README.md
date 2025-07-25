# Hashicorp Vault
## Tipos de secretos

### 1. **`Cubbyhole`**
- **Descripción**:
El backend `Cubbyhole` es un espacio temporal de almacenamiento asociado a un token en particular. Cada token en Vault tiene su propio espacio `Cubbyhole`, al cual **ningún otro token** puede acceder, ni siquiera el token raíz (_root token_).
- **Propiedades clave**:
    - Es privado y solo es accesible por el token que lo crea.
    - El contenido almacenado en `Cubbyhole` desaparece cuando el token asociado caduca.
    - No está diseñado para almacenamiento de datos extensivo, sino para **almacenamiento temporal**.
    - Muy usado para almacenar datos en un flujo de autenticación transitivo (como parte de login o MFA).

- **Casos de uso**:
    - _Temporal Storage_: Guardar datos temporales que deben permanecer completamente privados, como un token que será utilizado solo en una sesión específica.
    - **Token Wrapping**: Proteger temporalmente un secreto envuelto y pasarlo de manera segura a un cliente.

### 2. **(Key-Value Secrets Engine)`KV`**
- **Descripción**:
El backend es un sistema de almacenamiento genérico basado en pares clave-valor, ideal para almacenar secretos definidos por el usuario. Es uno de los métodos más comunes para manejar secretos en Vault. `KV`
- **Propiedades clave**:
    - **Versionado (KV v2)**: Permite mantener múltiples versiones de un secreto. Puedes recuperar versiones previas o eliminar de manera permanente un secreto.
    - Proporciona **lectura** y **escritura** para múltiples tokens usuarios, según las políticas configuradas.
    - Los datos almacenados persisten a menos que sean eliminados explícitamente.
    - Configurable para adaptarse a necesidades como TTL (Time to Live) o control de versiones.

- **Casos de uso**:
    - Almacenamiento estático de secretos como contraseñas, credenciales o claves de configuración.
    - **Versioned Secrets**: Manejo de secretos que pueden actualizarse y requieren gestión de versiones.
    - Usado frecuentemente en aplicaciones que necesitan acceder a secretos durante la ejecución.

### 3. **`Secrets`**
- **Descripción**:
`Secrets` es un término genérico que se usa en Vault para describir cualquier dato o secreto que Vault pueda almacenar, generar o manejar. No es un "backend" específico, sino una representación general de cómo se administran los datos en Vault.
- **Categorías comunes de `Secrets`**:
    - `Static Secrets`: Secretos estáticos que no cambian frecuentemente, como contraseñas almacenadas en el backend . `KV`
    - `Dynamic Secrets`: Credenciales temporales generadas en tiempo de ejecución por un plugin de Vault (por ejemplo, crear usuarios temporales en una base de datos).
    - `Cubbyhole Secrets`: Almacenamiento temporal de secretos vinculados a un token.

- **Ejemplos**:
    - Información almacenada en el backend de . `KV`
    - Credenciales temporales para bases de datos generadas dinámicamente.

- **Casos de uso**:
    - Es el fundamento para cualquier secreto que quieras manejar en Vault, ya sea estático, dinámico o temporal.

### Comparación Rápida:

| Característica | **Cubbyhole** | **KV (Key-Value)** | **Secrets** |
| --- | --- | --- | --- |
| **Propósito** | Almacenamiento temporal | Almacenamiento estático | Genérico (todos los secretos) |
| **Duración de almacenamiento** | Asociado al token (expira con este) | Persistente | Depende del backend |
| **Uso principal** | Flujo de autenticación y token wrapping | Guardar pares clave-valor como contraseñas o claves | Manejo de cualquier secreto |
| **Privacidad/Acceso** | Exclusivo del token | Basado en políticas | Depende del backend |
| **Versionado** | No | Sí (v2) | Depende del backend |
### Ejemplos de Uso:
1. **Cubbyhole**:
    - En token wrapping: Un cliente A genera un secreto que debe ser consumido por el cliente B. Se almacena en el cubbyhole y se pasa un token envuelto que solo el cliente B puede desempaquetar.

2. **KV**:
    - Almacenamiento estático: Una aplicación guarda sus credenciales de base de datos y las rota manual o automáticamente, utilizando el backend versionado (`kv v2`).

3. **Secrets**:
    - Manejo dinámico de credenciales: Un plugin de Vault genera un usuario temporal en una base de datos con permisos limitados.



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
