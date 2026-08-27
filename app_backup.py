import streamlit as st
import pandas as pd

from src.analysis import load_data, calculate_kpis, detect_anomalies
from src.ai_summary import generate_executive_summary

st.set_page_config(
    page_title="DataPulse AI",
    page_icon="📊",
    layout="wide",
)

st.title("DataPulse AI")
st.caption("Dashboard de análise de vendas com Python, SQL, Pandas e IA")

df = load_data()

with st.sidebar:
    st.header("Filtros")
    channels = st.multiselect(
        "Canal",
        sorted(df["channel"].unique()),
        default=sorted(df["channel"].unique()),
    )
    regions = st.multiselect(
        "Região",
        sorted(df["region"].unique()),
        default=sorted(df["region"].unique()),
    )

filtered = df[
    df["channel"].isin(channels) &
    df["region"].isin(regions)
].copy()

kpis = calculate_kpis(filtered)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Receita", f"R$ {kpis['revenue']:,.2f}")
c2.metric("Pedidos", f"{kpis['orders']:,}")
c3.metric("Ticket médio", f"R$ {kpis['average_ticket']:,.2f}")
c4.metric("Margem", f"{kpis['margin_rate']:.2f}%")

st.divider()

monthly = (
    filtered.assign(month=filtered["date"].dt.to_period("M").astype(str))
            .groupby("month")["revenue"]
            .sum()
)
st.subheader("Evolução da receita")
st.line_chart(monthly)

left, right = st.columns(2)

with left:
    st.subheader("Receita por canal")
    channel = filtered.groupby("channel")["revenue"].sum().sort_values(ascending=False)
    st.bar_chart(channel)

with right:
    st.subheader("Receita por região")
    region = filtered.groupby("region")["revenue"].sum().sort_values(ascending=False)
    st.bar_chart(region)

st.subheader("Produtos com maior faturamento")
products = (
    filtered.groupby(["product", "category"], as_index=False)
            .agg(
                revenue=("revenue", "sum"),
                quantity=("quantity", "sum"),
                margin=("margin", "sum")
            )
            .sort_values("revenue", ascending=False)
)
st.dataframe(products, use_container_width=True)

st.subheader("Anomalias")
anomalies = detect_anomalies(filtered)
st.dataframe(
    anomalies[
        ["order_id", "date", "channel", "region", "product", "revenue", "reason"]
    ],
    use_container_width=True,
)

st.subheader("Resumo executivo com IA")
if st.button("Gerar análise"):
    st.write(generate_executive_summary())
else:
    st.info("Opcional: configure a API de IA para habilitar esta funcionalidade.")
