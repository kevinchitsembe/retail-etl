#BillionairForever
import os
import requests
import msal
from config.settings import (
    ONEDRIVE_CLIENT_ID,
    ONEDRIVE_CLIENT_SECRET,
    ONEDRIVE_TENANT_ID,
    ONEDRIVE_REFRESH_TOKEN
)

GRAPH_URL = "https://graph.microsoft.com/v1.0"
ONEDRIVE_FOLDER = "RetailETL"

def get_access_token():
    app = msal.ConfidentialClientApplication(
        client_id=ONEDRIVE_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{ONEDRIVE_TENANT_ID}",
        client_credential=ONEDRIVE_CLIENT_SECRET,
    )

    result = app.acquire_token_by_refresh_token(
        refresh_token=ONEDRIVE_REFRESH_TOKEN,
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in result:
        raise Exception(f"Erro ao obter access token: {result}")

    return result["access_token"]

def upload_outputs(output_files: dict):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Garantir pasta
    folder_url = f"{GRAPH_URL}/me/drive/root/children"
    requests.post(
        folder_url,
        headers=headers,
        json={
            "name": ONEDRIVE_FOLDER,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "ignore"
        }
    )

    for name, path in output_files.items():
        file_name = os.path.basename(path)
        upload_url = (
            f"{GRAPH_URL}/me/drive/root:/{ONEDRIVE_FOLDER}/{file_name}:/content"
        )

        with open(path, "rb") as f:
            response = requests.put(upload_url, headers=headers, data=f)

        if response.status_code not in (200, 201):
            raise Exception(
                f"Erro ao fazer upload de {file_name}: {response.text}"
            )
