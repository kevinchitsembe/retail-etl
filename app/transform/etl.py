#BillionairForever
import os
import pandas as pd
from config.settings import TMP_OUTPUT

def run_etl(input_files):
    os.makedirs(TMP_OUTPUT, exist_ok=True)

    vendas_path = input_files.get("Vendas_Coerentes_Fix.csv")
    produtos_path = input_files.get("Produtos.xlsx")

    if not vendas_path or not produtos_path:
        raise Exception("Ficheiros de input obrigatórios não encontrados.")

    # Load
    df_vendas = pd.read_csv(vendas_path)
    df_produtos = pd.read_excel(produtos_path)

    # Normalize columns
    df_vendas.columns = df_vendas.columns.str.strip()
    df_produtos.columns = df_produtos.columns.str.strip()

    # Fact Sales
    fact_sales = df_vendas.copy()
    fact_sales["Date"] = pd.to_datetime(fact_sales["Date"])

    # Dim Products
    dim_products = df_produtos.copy()

    # Save outputs
    fact_path = os.path.join(TMP_OUTPUT, "fact_sales.csv")
    dim_path = os.path.join(TMP_OUTPUT, "dim_products.csv")

    fact_sales.to_csv(fact_path, index=False)
    dim_products.to_csv(dim_path, index=False)

    from transform.kpis import build_kpis
    kpi_path = build_kpis(fact_sales)

    return {
        "fact_sales": fact_path,
        "dim_products": dim_path,
        "kpi_sales": kpi_path
    }
