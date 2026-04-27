import duckdb
import os


def load_data():
    os.makedirs("data/gold", exist_ok=True)

    silver_data = duckdb.read_parquet("data/silver/electronics_sales_cleaned.parquet")

    monthly_evolution = silver_data.aggregate(
        """order_year_month,
        sum(net_revenue) AS faturamento_total, 
        sum(quantity) AS qtd_total, 
        avg(discount_pct) AS desconto_medio, 
        sum(net_revenue) / count(distinct order_id) AS ticket_medio,
        sum(ebitda) AS ebitda_total,
        sum(net_income) AS lucro_liquido_total"""
    ).order("order_year_month")


if __name__ == "__main__":
    load_data()
