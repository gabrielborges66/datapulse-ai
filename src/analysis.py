from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from .config import DATA_PATH, REPORTS_PATH
from .database import load_csv_to_sqlite, query

def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

def calculate_kpis(df: pd.DataFrame) -> dict:
    revenue = df["revenue"].sum()
    orders = df["order_id"].nunique()
    margin = df["margin"].sum()

    return {
        "revenue": round(float(revenue), 2),
        "orders": int(orders),
        "average_ticket": round(float(revenue / orders), 2) if orders else 0,
        "margin": round(float(margin), 2),
        "margin_rate": round(float(margin / revenue * 100), 2) if revenue else 0,
    }

def calculate_business_insights(df: pd.DataFrame) -> dict:
    total_revenue = df["revenue"].sum()

    # Receita e participação por canal
    channel_revenue = (
        df.groupby("channel")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    channel_share = (
        channel_revenue / total_revenue * 100
    ).round(2)

    # Receita e participação por região
    region_revenue = (
        df.groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    region_share = (
        region_revenue / total_revenue * 100
    ).round(2)

    # Ranking de produtos
    product_revenue = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    product_share = (
        product_revenue / total_revenue * 100
    ).round(2)

    return {
        "channel_revenue": channel_revenue,
        "channel_share": channel_share,
        "region_revenue": region_revenue,
        "region_share": region_share,
        "product_revenue": product_revenue,
        "product_share": product_share,
    }

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    q1 = df["revenue"].quantile(0.25)
    q3 = df["revenue"].quantile(0.75)
    iqr = q3 - q1
    upper_limit = q3 + 1.5 * iqr

    anomalies = df[df["revenue"] > upper_limit].copy()
    anomalies["upper_limit"] = upper_limit
    anomalies["reason"] = "Receita acima do limite superior do IQR"
    return anomalies.sort_values("revenue", ascending=False)

def run_analysis() -> dict:
    df = load_data()
    kpis = calculate_kpis(df)

    monthly = (
        df.groupby("month", as_index=False)
          .agg(revenue=("revenue", "sum"), margin=("margin", "sum"))
          .sort_values("month")
    )

    by_channel = (
        df.groupby("channel", as_index=False)
          .agg(
              revenue=("revenue", "sum"),
              orders=("order_id", "nunique"),
              margin=("margin", "sum")
          )
          .sort_values("revenue", ascending=False)
    )

    by_region = (
        df.groupby("region", as_index=False)
          .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
          .sort_values("revenue", ascending=False)
    )

    top_products = (
        df.groupby(["product", "category"], as_index=False)
          .agg(
              revenue=("revenue", "sum"),
              quantity=("quantity", "sum"),
              margin=("margin", "sum")
          )
          .sort_values("revenue", ascending=False)
          .head(10)
    )

    anomalies = detect_anomalies(df)

    monthly.to_csv(REPORTS_PATH / "monthly_kpis.csv", index=False)
    by_channel.to_csv(REPORTS_PATH / "channel_kpis.csv", index=False)
    by_region.to_csv(REPORTS_PATH / "region_kpis.csv", index=False)
    top_products.to_csv(REPORTS_PATH / "top_products.csv", index=False)
    anomalies.to_csv(REPORTS_PATH / "anomalies.csv", index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(monthly["month"], monthly["revenue"], marker="o")
    plt.title("Receita mensal")
    plt.xlabel("Mês")
    plt.ylabel("Receita")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(REPORTS_PATH / "monthly_revenue.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(by_channel["channel"], by_channel["revenue"])
    plt.title("Receita por canal")
    plt.xlabel("Canal")
    plt.ylabel("Receita")
    plt.tight_layout()
    plt.savefig(REPORTS_PATH / "revenue_by_channel.png", dpi=160)
    plt.close()

    # Load the synthetic dataset into SQLite before running SQL queries.
    load_csv_to_sqlite()

    # Demonstration SQL result.
    sql_top = query("""
        SELECT product,
               SUM(revenue) AS revenue,
               SUM(margin) AS margin,
               SUM(quantity) AS quantity
        FROM sales
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 10;
    """)
    sql_top.to_csv(REPORTS_PATH / "sql_top_products.csv", index=False)

    return {
        "kpis": kpis,
        "monthly": monthly,
        "by_channel": by_channel,
        "by_region": by_region,
        "top_products": top_products,
        "anomalies": anomalies,
    }

if __name__ == "__main__":
    result = run_analysis()
    print("DataPulse AI — análise concluída")
    print(f"Pedidos: {result['kpis']['orders']}")
    print(f"Receita: R$ {result['kpis']['revenue']:,.2f}")
    print(f"Ticket médio: R$ {result['kpis']['average_ticket']:,.2f}")
    print(f"Margem: {result['kpis']['margin_rate']:.2f}%")
    print(f"Anomalias: {len(result['anomalies'])}")
