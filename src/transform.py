import duckdb
import os


def transform_data():
    os.makedirs("data/silver", exist_ok=True)

    bronze_data = duckdb.read_parquet("data/bronze/electronics_sales_raw.parquet")

    silver_data = bronze_data.project(
        """
            * EXCLUDE (first_purchase_date, last_purchase_date, order_date), 
            first_purchase_date::DATE AS first_purchase_date, 
            last_purchase_date::DATE AS last_purchase_date,
            order_date::DATE AS order_date,
            churn_flag::BOOLEAN AS churn_flag
        """
    ).filter(
        """
            quantity > 0
            AND TRIM(customer_id) != ''
            AND TRIM(product_id) != ''
            AND unit_price > 0
            AND order_id IS NOT NULL    
            AND churn_flag IN (TRUE, FALSE)
        """
    )

    silver_data.write_parquet("data/silver/electronics_sales_cleaned.parquet")


if __name__ == "__main__":
    transform_data()
