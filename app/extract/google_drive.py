import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

def download_inputs():
    os.makedirs("input_data", exist_ok=True)
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    folder_id = os.getenv("GOOGLE_FOLDER_ID")

    creds_dict = json.loads(creds_json)

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )

    service = build("drive", "v3", credentials=credentials)

    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])
    downloaded_files = {}  # ← AGORA É UM DICIONÁRIO!

    for file in files:
        file_name = file["name"]
        file_path = os.path.join("input_data", file_name)  # ← CAMINHO COMPLETO
        
        request = service.files().get_media(fileId=file["id"])
        fh = io.FileIO(file_path, "wb")  # ← Usar o caminho completo
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Adicionar ao dicionário: {nome_arquivo: caminho_completo}
        downloaded_files[file_name] = file_path

    return downloaded_files  # ← Retorna dicionário
