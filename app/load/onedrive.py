import requests
import os

# =========================
# ENVIRONMENT VARIABLES
# =========================
TENANT_ID = os.getenv("ONEDRIVE_TENANT_ID")
CLIENT_ID = os.getenv("ONEDRIVE_CLIENT_ID")
CLIENT_SECRET = os.getenv("ONEDRIVE_CLIENT_SECRET")
FOLDER_PATH = os.getenv("ONEDRIVE_FOLDER_PATH")
USER_ID = os.getenv("ONEDRIVE_USER_ID")

# =========================
# VALIDATION (FAIL FAST)
# =========================
required_envs = {
    "ONEDRIVE_TENANT_ID": TENANT_ID,
    "ONEDRIVE_CLIENT_ID": CLIENT_ID,
    "ONEDRIVE_CLIENT_SECRET": CLIENT_SECRET,
    "ONEDRIVE_FOLDER_PATH": FOLDER_PATH,
    "ONEDRIVE_USER_ID": USER_ID,
}

for name, value in required_envs.items():
    if not value:
        raise EnvironmentError(f"Variável de ambiente não definida: {name}")

# =========================
# CONSTANTS
# =========================
AUTH_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
GRAPH_URL = "https://graph.microsoft.com/v1.0"


# =========================
# AUTHENTICATION
# =========================
def get_access_token():
    response = requests.post(
        AUTH_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


# =========================
# UPLOAD SINGLE FILE
# =========================
def upload_file(file_path, file_name):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }

    upload_url = (
        f"{GRAPH_URL}/users/{USER_ID}"
        f"/drive/root:{FOLDER_PATH}/{file_name}:/content"
    )

    with open(file_path, "rb") as f:
        response = requests.put(upload_url, headers=headers, data=f, timeout=60)

    response.raise_for_status()


# =========================
# UPLOAD MULTIPLE FILES
# =========================
def upload_outputs(files):
    """
    Recebe:
    - list: ["output/fact_sales.xlsx", ...]
    - dict: {"fact_sales": "output/fact_sales.xlsx", ...}
    """

    # Caso venha como dict
    if isinstance(files, dict):
        for file_path in files.values():
            file_name = os.path.basename(file_path)
            upload_file(file_path, file_name)

    # Caso venha como list
    elif isinstance(files, list):
        for file_path in files:
            file_name = os.path.basename(file_path)
            upload_file(file_path, file_name)

    else:
        raise TypeError("upload_outputs espera list ou dict de caminhos de ficheiros")
