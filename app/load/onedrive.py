import requests
import os

TENANT_ID = os.getenv("ONEDRIVE_TENANT_ID")
CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID")
CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET")
FOLDER_PATH = os.getenv("ONEDRIVE_FOLDER_PATH")

AUTH_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
GRAPH_URL = "https://graph.microsoft.com/v1.0"


def get_access_token():
    response = requests.post(
        AUTH_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def upload_file(file_path, file_name):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }

    upload_url = (
        f"{GRAPH_URL}/me/drive/root:"
        f"{FOLDER_PATH}/{file_name}:/content"
    )

    with open(file_path, "rb") as f:
        response = requests.put(upload_url, headers=headers, data=f)

    response.raise_for_status()


def upload_outputs(files):
    """
    Recebe um dicionário ou lista de ficheiros gerados pelo ETL
    e faz upload para o OneDrive.
    """

    # Se vier como dict {nome: path}
    if isinstance(files, dict):
        for _, file_path in files.items():
            file_name = os.path.basename(file_path)
            upload_file(file_path, file_name)

    # Se vier como lista ["fact_sales.csv", ...]
    elif isinstance(files, list):
        for file_path in files:
            file_name = os.path.basename(file_path)
            upload_file(file_path, file_name)

    else:
        raise TypeError("upload_outputs espera dict ou list de ficheiros")
