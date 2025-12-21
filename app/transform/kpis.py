#BillionairForever
import os
import pandas as pd
from config.settings import TMP_OUTPUT

def build_kpis(fact_sales: pd.DataFrame):
    kpis = (
        fact_sales
        .groupby("Date")
        .agg(
            TotalSales=("Total", "sum"),
            TotalQuantity=("Quantity", "sum")
        )
        .reset_index()
    )

    kpi_path = os.path.join(TMP_OUTPUT, "kpi_sales.csv")
    kpis.to_csv(kpi_path, index=False)

    return kpi_path
