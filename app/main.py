# BillionairForever 🚀

from extract.google_drive import download_inputs
from transform.etl import run_etl
from load.onedrive import upload_outputs
from utils.logger import get_logger

logger = get_logger()


def main():
    logger.info("🚀 ETL iniciado")

    logger.info("⬇️ A extrair dados do Google Drive")
    input_files = download_inputs()

    logger.info("🔄 A transformar dados e criar KPIs")
    output_files = run_etl(input_files)
    # output_files = ["fact_sales.xlsx", "dim_products.xlsx", "kpi_sales.xlsx"]

    logger.info("☁️ A carregar dados no OneDrive")
    upload_outputs(output_files)

    logger.info("✅ ETL finalizado com sucesso")


if __name__ == "__main__":
    main()
