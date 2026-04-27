import duckdb
import os


def load_data():
    os.makedirs("data/gold", exist_ok=True)

    con = duckdb.connect("data/gold/sales_analytics.duckdb")

    silver_data = con.read_parquet("data/silver/electronics_sales_cleaned.parquet")

    monthly_evolution = silver_data.aggregate(
        """
        order_year_month,
        sum(net_revenue) AS faturamento_total, 
        sum(quantity) AS qtd_total, 
        avg(discount_pct) AS desconto_medio, 
        sum(net_revenue) / count(distinct order_id) AS ticket_medio,
        sum(ebitda) AS ebitda_total,
        sum(net_income) AS lucro_liquido_total
        """
    ).order("order_year_month")

    product_performance = silver_data.aggregate(
        """
        category, 
        brand, 
        sum(net_revenue) AS faturamento_total, 
        sum(gross_profit) AS lucro_total,
        sum(quantity) AS qtd_total,
        (sum(net_revenue) / count(distinct order_id)) AS ticket_medio
        """
    ).order("faturamento_total DESC")

    customer_orders = silver_data.aggregate(
        "customer_id, count(distinct order_id) as total_orders"
    )

    status_client = customer_orders.project("""*, 
                            CASE 
                                WHEN total_orders = 1 THEN 'Cliente novo/único'
                                ELSE 'Cliente recorrente/fiel'
                            END AS status_cliente
                               """)

    recurrence_summary = status_client.aggregate(
        "status_cliente, count(customer_id) AS total_clientes"
    )

    monthly_evolution.write_parquet("data/gold/monthly_evolution.parquet")
    product_performance.write_parquet("data/gold/product_performance.parquet")
    recurrence_summary.write_parquet("data/gold/recurrence_summary.parquet")

    con.execute(
        "CREATE OR REPLACE TABLE evolucao_mensal AS SELECT * FROM monthly_evolution"
    )
    con.execute(
        "CREATE OR REPLACE TABLE performance_produtos AS SELECT * FROM product_performance"
    )
    con.execute(
        "CREATE OR REPLACE TABLE resumo_recorrencia AS SELECT * FROM recurrence_summary"
    )

    print("\n--- Resumo da Carga Gold ---")
    print(con.execute("SHOW TABLES").fetchall())
    con.close()

    print("Todas as tabelas foram salvas com sucesso.")


if __name__ == "__main__":
    load_data()
