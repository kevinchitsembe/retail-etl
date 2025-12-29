#BillionairForever
import os
import requests
import msal
import logging
from config.settings import (
    ONEDRIVE_CLIENT_ID,
    ONEDRIVE_CLIENT_SECRET,
    ONEDRIVE_TENANT_ID,
    #REMOVA ONEDRIVE_REFRESH_TOKEN - não é necessário para Client Credentials
)

logger = logging.getLogger(__name__)

GRAPH_URL = "https://graph.microsoft.com/v1.0"
ONEDRIVE_FOLDER = "RetailETL"
SCOPES = ["https://graph.microsoft.com/.default"]  # Scope para Client Credentials

def get_access_token():
    """Obtém access token usando Client Credentials Flow (server-side)"""
    try:
        logger.info("Obtendo access token via Client Credentials Flow...")
        
        app = msal.ConfidentialClientApplication(
            client_id=ONEDRIVE_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{ONEDRIVE_TENANT_ID}",
            client_credential=ONEDRIVE_CLIENT_SECRET,
        )

        # Client Credentials Flow - para aplicações server-side
        result = app.acquire_token_for_client(scopes=SCOPES)
        
        if "access_token" in result:
            logger.info("Access token obtido com sucesso")
            return result["access_token"]
        else:
            error_msg = result.get("error_description", str(result))
            logger.error(f"Falha na autenticação: {error_msg}")
            raise Exception(f"Erro ao obter access token: {error_msg}")
            
    except Exception as e:
        logger.error(f"Exceção em get_access_token: {str(e)}")
        raise

def upload_outputs(output_files: dict):
    """Upload dos arquivos processados para o OneDrive/SharePoint"""
    try:
        token = get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Preparando upload de {len(output_files)} arquivos...")
        
        # 1. Criar pasta (se não existir)
        folder_url = f"{GRAPH_URL}/me/drive/root/children"
        folder_payload = {
            "name": ONEDRIVE_FOLDER,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        
        try:
            folder_response = requests.post(folder_url, headers=headers, json=folder_payload)
            if folder_response.status_code == 409:
                logger.info(f"Pasta '{ONEDRIVE_FOLDER}' já existe")
            elif folder_response.status_code in (200, 201):
                logger.info(f"Pasta '{ONEDRIVE_FOLDER}' criada com sucesso")
            else:
                logger.warning(f"Resposta inesperada ao criar pasta: {folder_response.status_code}")
        except Exception as e:
            logger.warning(f"Erro ao verificar/criar pasta: {str(e)}")
            # Continuar mesmo se falhar - talvez a pasta já exista
        
        # 2. Fazer upload dos arquivos
        for file_type, file_path in output_files.items():
            if not os.path.exists(file_path):
                logger.error(f"Arquivo não encontrado: {file_path}")
                continue
                
            file_name = os.path.basename(file_path)
            logger.info(f"Fazendo upload de {file_name}...")
            
            # URL para upload
            upload_url = f"{GRAPH_URL}/me/drive/root:/{ONEDRIVE_FOLDER}/{file_name}:/content"
            
            try:
                with open(file_path, "rb") as f:
                    response = requests.put(
                        upload_url, 
                        headers={"Authorization": f"Bearer {token}"},  # Só authorization header
                        data=f.read()
                    )
                
                if response.status_code in (200, 201):
                    logger.info(f"✅ {file_name} upload completo")
                else:
                    logger.error(f"❌ Erro ao fazer upload de {file_name}: {response.status_code} - {response.text}")
                    # Não levantar exceção imediatamente, tentar outros arquivos
                    
            except Exception as e:
                logger.error(f"Erro ao processar {file_name}: {str(e)}")
                
        logger.info("Processo de upload finalizado")
        
    except Exception as e:
        logger.error(f"Erro crítico no upload: {str(e)}")
        raise
