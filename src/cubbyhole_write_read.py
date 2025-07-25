import os

import hvac
from dotenv import load_dotenv

load_dotenv("./config/.env.secrets")

VAULT_ADDR = os.getenv("VAULT_ADDR")
VAULT_ROOT_TOKEN = os.getenv("VAULT_ROOT_TOKEN")

# Datos del secreto a almacenar
SECRETO_PATH = "cubbyhole/mi_secreto_personal"
SECRETO_DATA = {
    "usuario": "usuario_ejemplo",
    "password": "mi_password_segura_123!"
}


def almacenar_secreto_en_cubbyhole():
    """
    Almacena un secreto en el cubbyhole de HashiCorp Vault.
    """
    try:
        # Inicializar el cliente de HVAC
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        # Verificar si el cliente está autenticado
        if not client.is_authenticated():
            print("Error: No se pudo autenticar con Vault. Verifique el token y la URL.")
            return

        print(f"Conectado a Vault en: {VAULT_ADDR}")

        write_response = client.write(SECRETO_PATH, **SECRETO_DATA)

        print(f"Secreto almacenado exitosamente en: {SECRETO_PATH}")
        print("Respuesta de Vault al escribir:", write_response)

    except hvac.exceptions.VaultError as e:
        print(f"Error de Vault: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


def leer_secreto_de_cubbyhole():
    """
    Lee un secreto almacenado en el cubbyhole de HashiCorp Vault.
    """
    try:
        # Inicializar el cliente de HVAC
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_ROOT_TOKEN)

        # Verificar si el cliente está autenticado
        if not client.is_authenticated():
            print("Error: No se pudo autenticar con Vault. Verifique el token y la URL.")
            return None

        print(f"Conectado a Vault en: {VAULT_ADDR}")

        # Leer el secreto del cubbyhole
        # Para el cubbyhole, se usa el método 'read' directamente
        read_response = client.read(SECRETO_PATH)

        if read_response is None:
            print(f"No se encontró ningún secreto en la ruta: {SECRETO_PATH}")
            return None

        # Los datos del secreto están en la clave 'data' de la respuesta
        secreto_leido = read_response['data']
        print(f"Secreto leído exitosamente de: {SECRETO_PATH}")
        print("Datos del secreto:")
        for key, value in secreto_leido.items():
            # Para la contraseña, podrías querer ocultar su valor real en la salida
            if key == "password":
                print(f"  {key}: {'*' * len(value)}")  # Muestra asteriscos en lugar de la contraseña real
            else:
                print(f"  {key}: {value}")

        return secreto_leido

    except hvac.exceptions.VaultError as e:
        print(f"Error de Vault: {e}")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return None


if __name__ == "__main__":
    almacenar_secreto_en_cubbyhole()

    secreto = leer_secreto_de_cubbyhole()

    if secreto:
        print("\nEl secreto se ha recuperado y se puede usar en tu aplicación.")
        # Ejemplo de cómo podrías usar los datos:
        # usuario = secreto.get('usuario')
        # password = secreto.get('password')
        # print(f"Usuario obtenido: {usuario}")
        # print(f"Contraseña obtenida: {password}") # ¡Cuidado al imprimir contraseñas!