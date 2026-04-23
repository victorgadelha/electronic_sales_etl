import duckdb
import os


def extract_data():
    os.makedirs("data/bronze", exist_ok=True)

    raw_data = duckdb.read_csv("data/bronze/electronics_sales_raw.csv")
    raw_data.write_parquet("data/bronze/electronics_sales_raw.parquet")

    print("Camada Bronze (Parquet) gerada com sucesso!")
    raw_data.show()


if __name__ == "__main__":
    extract_data()
