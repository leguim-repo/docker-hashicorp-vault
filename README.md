# Hashicorp Vault

## Tipos de secretos

### 1. **`Cubbyhole`**

- **Descripción**:
  El backend `Cubbyhole` es un espacio temporal de almacenamiento asociado a un token en particular. Cada token en Vault
  tiene su propio espacio `Cubbyhole`, al cual **ningún otro token** puede acceder, ni siquiera el token raíz (_root
  token_).
- **Propiedades clave**:
    - Es privado y solo es accesible por el token que lo crea.
    - El contenido almacenado en `Cubbyhole` desaparece cuando el token asociado caduca.
    - No está diseñado para almacenamiento de datos extensivo, sino para **almacenamiento temporal**.
    - Muy usado para almacenar datos en un flujo de autenticación transitivo (como parte de login o MFA).

- **Casos de uso**:
    - _Temporal Storage_: Guardar datos temporales que deben permanecer completamente privados, como un token que será
      utilizado solo en una sesión específica.
    - **Token Wrapping**: Proteger temporalmente un secreto envuelto y pasarlo de manera segura a un cliente.

### 2. **(Key-Value Secrets Engine)`KV`**

- **Descripción**:
  El backend es un sistema de almacenamiento genérico basado en pares clave-valor, ideal para almacenar secretos
  definidos por el usuario. Es uno de los métodos más comunes para manejar secretos en Vault. `KV`
- **Propiedades clave**:
    - **Versionado (KV v2)**: Permite mantener múltiples versiones de un secreto. Puedes recuperar versiones previas o
      eliminar de manera permanente un secreto.
    - Proporciona **lectura** y **escritura** para múltiples tokens usuarios, según las políticas configuradas.
    - Los datos almacenados persisten a menos que sean eliminados explícitamente.
    - Configurable para adaptarse a necesidades como TTL (Time to Live) o control de versiones.

- **Casos de uso**:
    - Almacenamiento estático de secretos como contraseñas, credenciales o claves de configuración.
    - **Versioned Secrets**: Manejo de secretos que pueden actualizarse y requieren gestión de versiones.
    - Usado frecuentemente en aplicaciones que necesitan acceder a secretos durante la ejecución.

### 3. **`Secrets`**

- **Descripción**:
  `Secrets` es un término genérico que se usa en Vault para describir cualquier dato o secreto que Vault pueda
  almacenar, generar o manejar. No es un "backend" específico, sino una representación general de cómo se administran
  los datos en Vault.
- **Categorías comunes de `Secrets`**:
    - `Static Secrets`: Secretos estáticos que no cambian frecuentemente, como contraseñas almacenadas en el backend .
      `KV`
    - `Dynamic Secrets`: Credenciales temporales generadas en tiempo de ejecución por un plugin de Vault (por ejemplo,
      crear usuarios temporales en una base de datos).
    - `Cubbyhole Secrets`: Almacenamiento temporal de secretos vinculados a un token.

- **Ejemplos**:
    - Información almacenada en el backend de . `KV`
    - Credenciales temporales para bases de datos generadas dinámicamente.

- **Casos de uso**:
    - Es el fundamento para cualquier secreto que quieras manejar en Vault, ya sea estático, dinámico o temporal.

### Comparación Rápida:

| Característica                 | **Cubbyhole**                           | **KV (Key-Value)**                                  | **Secrets**                   |
|--------------------------------|-----------------------------------------|-----------------------------------------------------|-------------------------------|
| **Propósito**                  | Almacenamiento temporal                 | Almacenamiento estático                             | Genérico (todos los secretos) |
| **Duración de almacenamiento** | Asociado al token (expira con este)     | Persistente                                         | Depende del backend           |
| **Uso principal**              | Flujo de autenticación y token wrapping | Guardar pares clave-valor como contraseñas o claves | Manejo de cualquier secreto   |
| **Privacidad/Acceso**          | Exclusivo del token                     | Basado en políticas                                 | Depende del backend           |
| **Versionado**                 | No                                      | Sí (v2)                                             | Depende del backend           |

### Ejemplos de Uso:

1. **Cubbyhole**:
    - En token wrapping: Un cliente A genera un secreto que debe ser consumido por el cliente B. Se almacena en el
      cubbyhole y se pasa un token envuelto que solo el cliente B puede desempaquetar.

2. **KV**:
    - Almacenamiento estático: Una aplicación guarda sus credenciales de base de datos y las rota manual o
      automáticamente, utilizando el backend versionado (`kv v2`).

3. **Secrets**:
    - Manejo dinámico de credenciales: Un plugin de Vault genera un usuario temporal en una base de datos con permisos
      limitados.

docker-compose up -d

# Verificar que Vault está en funcionamiento

docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault status

# Listar secretos

docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault kv list kv/

# Leer un secreto específico

docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault kv get kv/mi-app/desarrollo

# 1. **Obtener un valor específico** del secreto usando el formato

docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault kv get -field=db_usuario kv/mi-app/desarrollo

# 2. **Actualizar valores específicos** sin modificar los demás

docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault kv patch -mount=kv mi-app/desarrollo \
api_key="nueva-api-key"

# 3. **Ver el historial de versiones** del secreto:

docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault kv metadata get -mount=kv mi-app/desarrollo

# Crear el secreto de desarrollo

docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault kv put -mount=kv mi-app/desarrollo \
db_usuario="usuario_desarrollo" \
db_password="password_desarrollo" \
api_key="api-key-desarrollo"

# Crear el secreto de produccion

docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault kv put -mount=kv mi-app/produccion \
db_usuario="usuario_produccion" \
db_password="password_produccion" \
api_key="api-key-produccion"

# Verificar la conexión a la API de Vault

docker compose exec vault curl \
-H "X-Vault-Token: my_super_secret_root_token" \
http://127.0.0.1:8200/v1/sys/health

# Detener los contenedores

docker compose down -v

# Iniciar de nuevo

docker compose up -d

### 4. **`TOTP (Time-Based One-Time Password)`**

- **Descripción**:
  El motor de secretos TOTP permite a Vault actuar como proveedor de contraseñas de un solo uso basadas en tiempo. Este
  motor puede generar y validar tokens TOTP compatibles con aplicaciones de autenticación estándar como Google
  Authenticator o Authy.

- **Propiedades clave**:
    - Genera claves TOTP compatibles con estándares
    - Valida códigos TOTP
    - Integración con métodos de autenticación de Vault
    - Gestión centralizada de claves TOTP
    - Configurable para diferentes períodos y algoritmos

- **Casos de uso**:
    - Autenticación de dos factores (2FA)
    - Verificación adicional para accesos sensibles
    - Generación y validación de tokens temporales
    - MFA para acceso a recursos críticos

### Comandos básicos TOTP:

# Habilitar el motor TOTP

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault secrets enable totp
```

# Verifica que TOTP está habilitado:

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault secrets list

```

# Crear una nueva clave TOTP

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault write totp/keys/mi-app \
                    generate=true \
                    issuer="Mi Aplicación" \
                    account_name="usuario@ejemplo.com"
```

# Generar códigos TOTP

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault read totp/code/mi-app
```

# Validar un código TOTP

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault write totp/code/mi-app code="123456"
``` 

El motor TOTP se puede integrar con otros aspectos de Vault como políticas de acceso y autenticación multi-factor para
proporcionar una capa adicional de seguridad a tus aplicaciones y servicios.

# Ejecutar script test-totp.sh

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault sh /vault/scripts/test-totp.sh
```

# Listar las claves TOTP creadas

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault list totp/keys
```

# Ver la configuración de una clave TOTP específica

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault read totp/keys/test-app
```

# Si quieres generar un nuevo código TOTP en cualquier momento:

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault read totp/code/test-app
```

## Importar TOTP

# 1. **Importando una clave TOTP usando un secreto base32 existente**:

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault write totp/keys/mi-app-importada \
    key=BASE32_CLAVE_SECRETA \
    issuer="Mi Aplicación" \
    account_name="usuario@ejemplo.com" \
    algorithm=SHA1 \
    period=30 \
    digits=6
```

# 2. **Importando usando una URL de TOTP**:

```
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault write totp/keys/mi-app-importada \
    url="otpauth://totp/Mi%20Aplicacion:usuario@ejemplo.com?secret=TU_CLAVE_BASE32&issuer=Mi%20Aplicacion&algorithm=SHA1&digits=6&period=30"
```

Por ejemplo, si tienes una clave TOTP de Google Authenticator:

```
# Ejemplo con una clave BASE32 existente
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault write totp/keys/google-auth \
    key=JBSWY3DPEHPK3PXP \
    issuer="Google" \
    account_name="ejemplo@gmail.com"
```

Para verificar que se importó correctamente:

```
# Ver la configuración
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault read totp/keys/mi-app-importada

# Generar un código para probar
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault read totp/code/mi-app-importada

# Validar un código específico
docker compose exec -e VAULT_TOKEN=my_super_secret_root_token vault vault write totp/code/mi-app-importada code="123456"
```