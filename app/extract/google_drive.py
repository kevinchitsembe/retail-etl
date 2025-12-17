#BillionairForever
import os
import io
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from config.settings import GOOGLE_FOLDER_ID, GOOGLE_CREDENTIALS_JSON, TMP_INPUT

def download_inputs():
    os.makedirs(TMP_INPUT, exist_ok=True)

    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds = Credentials.from_authorized_user_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/drive.readonly"
    ])

    service = build("drive", "v3", credentials=creds)

    query = f"'{GOOGLE_FOLDER_ID}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        raise Exception("Nenhum ficheiro encontrado na pasta do Google Drive.")

    downloaded_files = {}

    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        request = service.files().get_media(fileId=file_id)

        file_path = os.path.join(TMP_INPUT, file_name)
        fh = io.FileIO(file_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        downloaded_files[file_name] = file_path

    return downloaded_files
