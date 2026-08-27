import streamlit as st
import pandas as pd

from src.analysis import (
    load_data,
    calculate_kpis,
    detect_anomalies,
    calculate_business_insights,
)
from src.ai_summary import generate_executive_summary

# ---------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------
st.set_page_config(
    page_title="DataPulse AI | Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Estilo visual
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.1rem;
        }

        .subtitle {
            color: #8f96a3;
            font-size: 1rem;
            margin-bottom: 1.2rem;
        }

        .section-label {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #8f96a3;
            margin-top: 0.5rem;
        }

        div[data-testid="stMetric"] {
            padding: 0.8rem 1rem;
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 12px;
        }

        .insight-box {
            padding: 1rem 1.1rem;
            border-radius: 12px;
            border: 1px solid rgba(128, 128, 128, 0.20);
            background: rgba(128, 128, 128, 0.05);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------
def brl(value: float) -> str:
    """Formata valores monetários no padrão brasileiro."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: float) -> str:
    """Formata percentual com duas casas."""
    return f"{value:.2f}%".replace(".", ",")


def empty_state(message: str) -> None:
    st.info(message)


# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------
st.markdown('<div class="main-title">📊 DataPulse AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Sales Analytics & Intelligence — Python, Pandas, SQL e IA</div>',
    unsafe_allow_html=True,
)

df = load_data()

# ---------------------------------------------------------
# Filtros
# ---------------------------------------------------------
with st.sidebar:
    st.header("Filtros")

    channels_available = sorted(df["channel"].dropna().unique())
    regions_available = sorted(df["region"].dropna().unique())

    channels = st.multiselect(
        "Canal",
        channels_available,
        default=channels_available,
    )

    regions = st.multiselect(
        "Região",
        regions_available,
        default=regions_available,
    )

    date_min = df["date"].min().date()
    date_max = df["date"].max().date()

    date_range = st.date_input(
        "Período",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    st.divider()

    st.caption("DataPulse AI")
    st.caption("Projeto de portfólio — dados sintéticos")

# ---------------------------------------------------------
# Tratamento do período
# ---------------------------------------------------------
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range
    end_date = date_range

filtered = df[
    df["channel"].isin(channels)
    & df["region"].isin(regions)
    & (df["date"].dt.date >= start_date)
    & (df["date"].dt.date <= end_date)
].copy()

# ---------------------------------------------------------
# Estado vazio
# ---------------------------------------------------------
if filtered.empty:
    st.warning(
        "Nenhum registro corresponde aos filtros selecionados. "
        "Escolha pelo menos um canal, uma região e um período válido."
    )
    st.stop()

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
kpis = calculate_kpis(filtered)
insights = calculate_business_insights(filtered)

st.markdown('<div class="section-label">Indicadores principais</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Receita", brl(kpis["revenue"]))
c2.metric("Pedidos", f'{kpis["orders"]:,}'.replace(",", "."))
c3.metric("Ticket médio", brl(kpis["average_ticket"]))
c4.metric("Margem", pct(kpis["margin_rate"]))

st.divider()

# ---------------------------------------------------------
# Evolução da receita
# ---------------------------------------------------------
st.subheader("Evolução da receita")

monthly = (
    filtered.assign(month=filtered["date"].dt.to_period("M").astype(str))
    .groupby("month")["revenue"]
    .sum()
    .sort_index()
)

st.line_chart(monthly, use_container_width=True)

# ---------------------------------------------------------
# Comparativos
# ---------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Receita por canal")
    channel = (
        filtered.groupby("channel")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(channel, use_container_width=True)

with right:
    st.subheader("Receita por região")
    region = (
        filtered.groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(region, use_container_width=True)


st.divider()

st.subheader("Top 5 produtos por receita")

top_products = (
    filtered.groupby("product")["revenue"]
    .sum()
    .sort_values(ascending=True)
    .tail(5)
)

st.bar_chart(
    top_products,
    horizontal=True,
    use_container_width=True
)

# ---------------------------------------------------------
# Produtos
# ---------------------------------------------------------
st.subheader("Top produtos por faturamento")

products = (
    filtered.groupby(["product", "category"], as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        quantity=("quantity", "sum"),
        margin=("margin", "sum"),
    )
    .sort_values("revenue", ascending=False)
    .head(10)
)

products_display = products.copy()
products_display["revenue"] = products_display["revenue"].map(brl)
products_display["margin"] = products_display["margin"].map(brl)

st.dataframe(
    products_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "product": "Produto",
        "category": "Categoria",
        "revenue": "Receita",
        "quantity": "Quantidade",
        "margin": "Margem",
    },
)

# ---------------------------------------------------------
# Anomalias
# ---------------------------------------------------------

st.subheader("Anomalias detectadas")

anomalies = detect_anomalies(filtered)

total_registros = len(filtered)
total_anomalias = len(anomalies)

receita_total = filtered["revenue"].sum()
receita_anomalias = anomalies["revenue"].sum()

percentual_anomalias = (
    total_anomalias / total_registros * 100
    if total_registros > 0
    else 0
)

percentual_receita_anomalias = (
    receita_anomalias / receita_total * 100
    if receita_total > 0
    else 0
)

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "Anomalias identificadas",
        f"{total_anomalias}",
        f"{percentual_anomalias:.1f}% dos registros",
        delta_color="inverse"
    )

with c2:
    st.metric(
        "Receita das anomalias",
        brl(receita_anomalias),
        f"{percentual_receita_anomalias:.1f}% da receita",
        delta_color="inverse"
    )

st.caption(
    f"{total_anomalias} registro(s) identificado(s) pelo método IQR."
)

if anomalies.empty:
    st.empty_state(
        "Nenhuma anomalia foi identificada nos filtros selecionados."
    )

else:
    anomalies_display = anomalies[
        [
            "order_id",
            "date",
            "channel",
            "region",
            "product",
            "revenue",
            "reason",
        ]
    ].copy()

    anomalies_display["date"] = (
        anomalies_display["date"]
        .dt.strftime("%d/%m/%Y")
    )

    anomalies_display["revenue"] = (
        anomalies_display["revenue"]
        .map(brl)
    )

    st.dataframe(
        anomalies_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "order_id": "Pedido",
            "date": "Data",
            "channel": "Canal",
            "region": "Região",
            "product": "Produto",
            "revenue": "Receita",
            "reason": "Motivo",
        },
    )

# ---------------------------------------------------------
# Anomalias por canal
# ---------------------------------------------------------

st.subheader("Anomalias por canal")

anomalies_by_channel = (
    anomalies
    .groupby("channel")
    .size()
    .sort_values(ascending=False)
)

st.bar_chart(
    anomalies_by_channel,
    use_container_width=True
)

# ---------------------------------------------------------
# Concentração das anomalias por canal
# ---------------------------------------------------------

if not anomalies.empty:
    canal_principal = anomalies_by_channel.index[0]
    qtd_canal_principal = anomalies_by_channel.iloc[0]

    percentual_canal_principal = (
        qtd_canal_principal / total_anomalias * 100
        if total_anomalias > 0
        else 0
    )

    st.info(
        f"O canal **{canal_principal}** concentra "
        f"**{percentual_canal_principal:.1f}%** das anomalias "
        f"identificadas ({qtd_canal_principal} de {total_anomalias} registros)."
    )

# ---------------------------------------------------------
# Anomalias por região
# ---------------------------------------------------------

st.subheader("Anomalias por região")

anomalies_by_region = (
    anomalies
    .groupby("region")
    .size()
    .sort_values(ascending=False)
)

st.bar_chart(
    anomalies_by_region,
    use_container_width=True
)

# ---------------------------------------------------------
# Concentração das anomalias por região
# ---------------------------------------------------------

if not anomalies.empty:
    regiao_principal = anomalies_by_region.index[0]
    qtd_regiao_principal = anomalies_by_region.iloc[0]

    percentual_regiao_principal = (
        qtd_regiao_principal / total_anomalias * 100
        if total_anomalias > 0
        else 0
    )

    st.info(
        f"A região **{regiao_principal}** concentra "
        f"**{percentual_regiao_principal:.1f}%** das anomalias "
        f"identificadas ({qtd_regiao_principal} de {total_anomalias} registros)."
    )

# ---------------------------------------------------------
# Resumo executivo
# ---------------------------------------------------------

st.subheader("Resumo executivo com IA")

with st.expander("O que este projeto analisa?"):
    st.markdown(
        """
        O **DataPulse AI** transforma dados de vendas em indicadores e
        insights para apoiar decisões de negócio.

        A análise combina:

        - **Python e Pandas** para tratamento e análise dos dados
        - **SQL/SQLite** para consultas
        - **Estatística descritiva e IQR** para identificação de anomalias
        - **Streamlit** para visualização interativa
        - **IA generativa** para elaboração do resumo executivo

        O resumo executivo é sempre gerado considerando os **filtros
        selecionados no dashboard**.
        """
    )


if st.button("Gerar análise executiva", type="primary"):

    try:
        # Gera a análise utilizando exatamente os dados filtrados
        summary = generate_executive_summary(filtered)

        # Limpeza de possíveis formatações indesejadas
        summary = summary.replace("R\\$", "R$")
        summary = summary.replace("\\$", "$")

        # Remove possíveis blocos de código Markdown
        summary = summary.replace("```markdown", "")
        summary = summary.replace("```", "")

        with st.container(border=True):

            st.markdown("### 🤖 Resumo executivo")

            st.markdown(summary)

    except Exception as exc:

        st.warning(
            "A análise executiva não pôde ser gerada no momento. "
            "O dashboard continua funcionando normalmente."
        )

        st.caption(f"Detalhe técnico: {exc}")

else:

    st.info(
        "A análise executiva é opcional. "
        "Clique no botão acima para gerar os insights "
        "considerando os filtros selecionados."
    )


# ---------------------------------------------------------
# Metodologia
# ---------------------------------------------------------

with st.expander("Metodologia da análise"):

    st.markdown(
        """
        **Fonte:** dados sintéticos de vendas.

        **Tecnologias:** Python, Pandas, SQL/SQLite e Streamlit.

        **KPIs analisados:**
        - Receita total
        - Número de pedidos
        - Ticket médio
        - Margem

        **Anomalias:** método estatístico IQR
        (Intervalo Interquartil), utilizado para identificar
        receitas acima do limite superior.

        **Análise executiva:** utiliza os dados resultantes dos
        filtros selecionados no dashboard para gerar achados,
        oportunidades, pontos de atenção e perguntas para
        investigação.

        **Objetivo:** demonstrar um fluxo de análise de dados de
        ponta a ponta, desde a preparação dos dados até a
        apresentação dos resultados e geração de insights.
        """
    )