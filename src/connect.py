import openeo
from dotenv import load_dotenv

load_dotenv()

OPENEO_BACKEND = "https://openeo.dataspace.copernicus.eu"

def get_openeo_connection() -> openeo.Connection:
    connection = openeo.connect(OPENEO_BACKEND)
    connection.authenticate_oidc()
    return connection
