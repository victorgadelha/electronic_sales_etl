import duckdb
import os


def transform_data():
    os.makedirs("data/silver", exist_ok=True)
    os.makedirs("data/quarantine", exist_ok=True)

    bronze_data = duckdb.read_parquet("data/bronze/electronics_sales_raw.parquet")

    base_silver = bronze_data.project(
        """
        * EXCLUDE (first_purchase_date, last_purchase_date, order_date, churn_flag), 
        first_purchase_date::DATE AS first_purchase_date, 
        last_purchase_date::DATE AS last_purchase_date,
        order_date::DATE AS order_date,
        churn_flag::BOOLEAN AS churn_flag,
        YEAR(order_date::DATE) AS order_year,
        MONTH(order_date::DATE) AS order_month,
        QUARTER(order_date::DATE) AS order_quarter,
        strftime(order_date::DATE, '%Y-%m') AS order_year_month
    """
    )

    regras_de_qualidade = """
        quantity > 0
        AND TRIM(customer_id) != ''
        AND TRIM(product_id) != ''
        AND unit_price > 0
        AND order_id IS NOT NULL    
        AND churn_flag IN (TRUE, FALSE)
    """

    silver_data = base_silver.filter(regras_de_qualidade)

    silver_data.write_parquet("data/silver/electronics_sales_cleaned.parquet")
    print("Dados VÁLIDOS salvos na Silver.")

    quarantine_data = base_silver.filter(f"NOT COALESCE({regras_de_qualidade}, FALSE)")

    quarantine_data.write_parquet("data/quarantine/rejeitados_silver.parquet")
    print("Dados INVÁLIDOS salvos na Quarentena.")


if __name__ == "__main__":
    transform_data()
