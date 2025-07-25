import hvac
import warnings

# Suprimir la advertencia de deprecación
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Crear cliente de Vault
client = hvac.Client(
    url='http://localhost:8200',
    token='mi_token_root'
)

def leer_secreto(path):
    """Función auxiliar para leer secretos de forma segura"""
    try:
        secreto = client.secrets.kv.v2.read_secret_version(
            mount_point='kv',
            path=path,
            raise_on_deleted_version=True
        )
        return secreto['data']['data']
    except hvac.exceptions.InvalidPath:
        print(f"No se encontró el secreto en la ruta: {path}")
        return None
    except Exception as e:
        print(f"Error al leer el secreto {path}: {str(e)}")
        return None

# Leer los secretos
secretos_dev = leer_secreto('mi-app/desarrollo')
if secretos_dev:
    print("Secretos de desarrollo:", secretos_dev)

secretos_prod = leer_secreto('mi-app/produccion')
if secretos_prod:
    print("Secretos de producción:", secretos_prod)
