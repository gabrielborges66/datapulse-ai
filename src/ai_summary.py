import os

from dotenv import load_dotenv

from .analysis import (
    load_data,
    calculate_kpis,
    detect_anomalies,
)

load_dotenv()


# ---------------------------------------------------------
# Formatação
# ---------------------------------------------------------

def format_brl(value: float) -> str:
    """
    Formata valores monetários no padrão brasileiro.

    Exemplo:
    12639.32 -> R$ 12.639,32
    """

    formatted = (
        f"{value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {formatted}"


def format_number(value: int) -> str:
    """
    Formata números no padrão brasileiro.

    Exemplo:
    1800 -> 1.800
    """

    return f"{value:,}".replace(",", ".")


def format_percentage(value: float) -> str:
    """
    Formata percentual no padrão brasileiro.
    """

    return f"{value:.1f}%"


# ---------------------------------------------------------
# Contexto para IA
# ---------------------------------------------------------

def build_context(df=None) -> str:
    """
    Constrói o contexto utilizado pela análise executiva.

    Todos os dados são calculados sobre o DataFrame recebido,
    portanto respeitam os filtros aplicados no dashboard.
    """

    if df is None:
        df = load_data()

    if df.empty:
        return "Não existem registros para os filtros selecionados."

    kpis = calculate_kpis(df)
    anomalies = detect_anomalies(df)

    # ---------------------------------------------------------
    # Receita por canal
    # ---------------------------------------------------------

    by_channel = (
        df.groupby("channel")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    # ---------------------------------------------------------
    # Receita por região
    # ---------------------------------------------------------

    by_region = (
        df.groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    # ---------------------------------------------------------
    # Receita por produto
    # ---------------------------------------------------------

    by_product = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    # ---------------------------------------------------------
    # Top 5 produtos
    # ---------------------------------------------------------

    top_products = by_product.head(5)

    # ---------------------------------------------------------
    # Receita das anomalias
    # ---------------------------------------------------------

    anomaly_revenue = (
        anomalies["revenue"].sum()
        if not anomalies.empty
        else 0
    )

    # ---------------------------------------------------------
    # Percentual das anomalias
    # ---------------------------------------------------------

    anomaly_percentage = (
        len(anomalies) / len(df) * 100
        if len(df) > 0
        else 0
    )

    # ---------------------------------------------------------
    # Participação do canal líder
    # ---------------------------------------------------------

    leader_channel = by_channel.index[0]
    leader_channel_revenue = by_channel.iloc[0]

    leader_channel_share = (
        leader_channel_revenue / kpis["revenue"] * 100
        if kpis["revenue"] > 0
        else 0
    )

    # ---------------------------------------------------------
    # Participação da região líder
    # ---------------------------------------------------------

    leader_region = by_region.index[0]
    leader_region_revenue = by_region.iloc[0]

    leader_region_share = (
        leader_region_revenue / kpis["revenue"] * 100
        if kpis["revenue"] > 0
        else 0
    )

    # ---------------------------------------------------------
    # Produto líder
    # ---------------------------------------------------------

    leader_product = by_product.index[0]
    leader_product_revenue = by_product.iloc[0]

    leader_product_share = (
        leader_product_revenue / kpis["revenue"] * 100
        if kpis["revenue"] > 0
        else 0
    )

    # ---------------------------------------------------------
    # Textos
    # ---------------------------------------------------------

    channels_text = "\n".join(
        f"- {channel}: {format_brl(revenue)}"
        for channel, revenue in by_channel.items()
    )

    regions_text = "\n".join(
        f"- {region}: {format_brl(revenue)}"
        for region, revenue in by_region.items()
    )

    products_text = "\n".join(
        f"- {product}: {format_brl(revenue)}"
        for product, revenue in top_products.items()
    )

    return f"""
DADOS DO ESCOPO ANALISADO

Quantidade de registros:
{format_number(len(df))}

KPIs:
- Receita total: {format_brl(kpis["revenue"])}
- Pedidos: {format_number(kpis["orders"])}
- Ticket médio: {format_brl(kpis["average_ticket"])}
- Margem: {format_percentage(kpis["margin_rate"])}

CANAIS ANALISADOS:
Quantidade de canais: {len(by_channel)}
Canal com maior receita: {leader_channel}
Receita do canal: {format_brl(leader_channel_revenue)}
Participação na receita: {format_percentage(leader_channel_share)}

RECEITA POR CANAL:
{channels_text}

REGIÕES ANALISADAS:
Quantidade de regiões: {len(by_region)}
Região com maior receita: {leader_region}
Receita da região: {format_brl(leader_region_revenue)}
Participação na receita: {format_percentage(leader_region_share)}

RECEITA POR REGIÃO:
{regions_text}

PRODUTO COM MAIOR RECEITA:
Produto: {leader_product}
Receita: {format_brl(leader_product_revenue)}
Participação na receita: {format_percentage(leader_product_share)}

TOP 5 PRODUTOS POR RECEITA:
{products_text}

ANOMALIAS:
- Quantidade: {format_number(len(anomalies))}
- Percentual dos registros: {format_percentage(anomaly_percentage)}
- Receita associada às anomalias: {format_brl(anomaly_revenue)}
"""


# ---------------------------------------------------------
# Análise local
# ---------------------------------------------------------

def generate_local_summary(df=None) -> str:
    """
    Gera uma análise executiva local sem depender da API da OpenAI.
    """

    if df is None:
        df = load_data()

    # ---------------------------------------------------------
    # Sem dados
    # ---------------------------------------------------------

    if df.empty:
        return """
### Principais achados

Não existem registros para os filtros selecionados.

### Oportunidades

Não foi possível identificar oportunidades sem dados no escopo analisado.

### Pontos de atenção

Não existem registros suficientes para realizar a análise.

### Próximas perguntas para investigação

- Existem dados disponíveis para o período selecionado?
- Os filtros correspondem ao escopo desejado?
"""

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------

    kpis = calculate_kpis(df)

    # ---------------------------------------------------------
    # Receita por canal
    # ---------------------------------------------------------

    by_channel = (
        df.groupby("channel")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    # ---------------------------------------------------------
    # Receita por região
    # ---------------------------------------------------------

    by_region = (
        df.groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    # ---------------------------------------------------------
    # Receita por produto
    # ---------------------------------------------------------

    by_product = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    # ---------------------------------------------------------
    # Anomalias
    # ---------------------------------------------------------

    anomalies = detect_anomalies(df)

    total_records = len(df)
    total_anomalies = len(anomalies)

    anomaly_revenue = (
        anomalies["revenue"].sum()
        if not anomalies.empty
        else 0
    )

    anomaly_percentage = (
        total_anomalies / total_records * 100
        if total_records > 0
        else 0
    )

    anomaly_revenue_percentage = (
        anomaly_revenue / kpis["revenue"] * 100
        if kpis["revenue"] > 0
        else 0
    )

    # ---------------------------------------------------------
    # Canal
    # ---------------------------------------------------------

    canal_lider = by_channel.index[0]
    receita_canal_lider = by_channel.iloc[0]

    participacao_canal = (
        receita_canal_lider / kpis["revenue"] * 100
        if kpis["revenue"] > 0
        else 0
    )

    # ---------------------------------------------------------
    # Região
    # ---------------------------------------------------------

    regiao_lider = by_region.index[0]
    receita_regiao_lider = by_region.iloc[0]

    participacao_regiao = (
        receita_regiao_lider / kpis["revenue"] * 100
        if kpis["revenue"] > 0
        else 0
    )

    # ---------------------------------------------------------
    # Produto
    # ---------------------------------------------------------

    produto_lider = by_product.index[0]
    receita_produto_lider = by_product.iloc[0]

    participacao_produto = (
        receita_produto_lider / kpis["revenue"] * 100
        if kpis["revenue"] > 0
        else 0
    )

    # ---------------------------------------------------------
    # Principais achados
    # ---------------------------------------------------------

    principais_achados = []

    principais_achados.append(
        f"A operação analisada apresentou receita total de "
        f"{format_brl(kpis['revenue'])}, distribuída em "
        f"{format_number(kpis['orders'])} pedidos, com ticket médio de "
        f"{format_brl(kpis['average_ticket'])}."
    )

    # Canal

    if len(by_channel) == 1:
        principais_achados.append(
            f"O escopo selecionado contém apenas o canal "
            f"{canal_lider}, responsável por toda a receita analisada."
        )
    else:
        principais_achados.append(
            f"O canal com maior receita foi {canal_lider}, "
            f"com {format_brl(receita_canal_lider)}, "
            f"representando {format_percentage(participacao_canal)} "
            f"da receita do escopo."
        )

    # Região

    if len(by_region) == 1:
        principais_achados.append(
            f"O escopo selecionado contém apenas a região "
            f"{regiao_lider}, responsável por toda a receita analisada."
        )
    else:
        principais_achados.append(
            f"A região com maior receita foi {regiao_lider}, "
            f"com {format_brl(receita_regiao_lider)}, "
            f"representando {format_percentage(participacao_regiao)} "
            f"do total."
        )

    principais_achados.append(
        f"O produto com maior participação na receita foi "
        f"{produto_lider}, com {format_brl(receita_produto_lider)}, "
        f"equivalente a {format_percentage(participacao_produto)} "
        f"da receita analisada."
    )

    principais_achados_text = "\n\n".join(principais_achados)

    # ---------------------------------------------------------
    # Oportunidades
    # ---------------------------------------------------------

    oportunidades = []

    # Comparação entre canais

    if len(by_channel) > 1:
        canal_menor = by_channel.index[-1]
        receita_canal_menor = by_channel.iloc[-1]

        diferenca_canais = (
            receita_canal_lider - receita_canal_menor
        )

        oportunidades.append(
            f"A diferença entre o canal com maior receita "
            f"({canal_lider}) e o menor ({canal_menor}) foi de "
            f"{format_brl(diferenca_canais)}, o que indica uma "
            f"oportunidade para investigar os fatores que explicam "
            f"essa diferença de desempenho."
        )

    # Comparação entre regiões

    if len(by_region) > 1:
        regiao_menor = by_region.index[-1]
        receita_regiao_menor = by_region.iloc[-1]

        diferenca_regioes = (
            receita_regiao_lider - receita_regiao_menor
        )

        oportunidades.append(
            f"A diferença entre a região com maior receita "
            f"({regiao_lider}) e a menor ({regiao_menor}) foi de "
            f"{format_brl(diferenca_regioes)}, indicando uma "
            f"oportunidade para investigar variações de desempenho "
            f"entre as localidades."
        )

    # Produto

    if participacao_produto >= 25:
        oportunidades.append(
            f"O produto {produto_lider} concentra "
            f"{format_percentage(participacao_produto)} da receita "
            f"analisada. Essa concentração pode ser acompanhada para "
            f"entender o impacto desse produto no resultado geral."
        )
    else:
        oportunidades.append(
            f"O produto {produto_lider} possui a maior receita do "
            f"escopo, com {format_percentage(participacao_produto)} "
            f"do total, sendo um item relevante para análise de "
            f"desempenho comercial."
        )

    if not oportunidades:
        oportunidades.append(
            "O escopo analisado possui pouca variação entre categorias, "
            "sendo recomendada a ampliação dos filtros para permitir "
            "comparações adicionais."
        )

    oportunidades_text = "\n\n".join(oportunidades)

    # ---------------------------------------------------------
    # Pontos de atenção
    # ---------------------------------------------------------

    pontos_atencao = []

    if total_anomalies > 0:
        pontos_atencao.append(
            f"Foram identificadas {format_number(total_anomalies)} "
            f"anomalias pelo método IQR, correspondentes a "
            f"{format_percentage(anomaly_percentage)} dos registros "
            f"analisados."
        )

        pontos_atencao.append(
            f"Essas anomalias representam "
            f"{format_brl(anomaly_revenue)} em receita, equivalente a "
            f"{format_percentage(anomaly_revenue_percentage)} da "
            f"receita do escopo."
        )

        # Canal com mais anomalias

        anomalies_by_channel = (
            anomalies.groupby("channel")
            .size()
            .sort_values(ascending=False)
        )

        if len(anomalies_by_channel) > 1:
            canal_anomalias = anomalies_by_channel.index[0]
            quantidade_canal_anomalias = anomalies_by_channel.iloc[0]

            pontos_atencao.append(
                f"O canal {canal_anomalias} apresentou a maior "
                f"quantidade de anomalias, com "
                f"{format_number(quantidade_canal_anomalias)} registros."
            )

        # Região com mais anomalias

        anomalies_by_region = (
            anomalies.groupby("region")
            .size()
            .sort_values(ascending=False)
        )

        if len(anomalies_by_region) > 1:
            regiao_anomalias = anomalies_by_region.index[0]
            quantidade_regiao_anomalias = anomalies_by_region.iloc[0]

            pontos_atencao.append(
                f"A região {regiao_anomalias} apresentou a maior "
                f"quantidade de anomalias, com "
                f"{format_number(quantidade_regiao_anomalias)} registros."
            )

    else:
        pontos_atencao.append(
            "Nenhuma anomalia foi identificada pelo método IQR "
            "no escopo analisado."
        )

    pontos_atencao_text = "\n\n".join(pontos_atencao)

    # ---------------------------------------------------------
    # Próximas perguntas
    # ---------------------------------------------------------

    perguntas = []

    if len(by_channel) > 1:
        perguntas.append(
            "Quais fatores explicam a diferença de receita entre os canais?"
        )

    if len(by_region) > 1:
        perguntas.append(
            "Quais fatores explicam as diferenças de desempenho entre as regiões?"
        )

    if participacao_produto >= 20:
        perguntas.append(
            f"A concentração de receita no produto {produto_lider} "
            "representa uma dependência relevante?"
        )
    else:
        perguntas.append(
            "Quais produtos apresentam maior potencial de crescimento?"
        )

    if total_anomalies > 0:
        perguntas.append(
            "As anomalias estão concentradas em produtos, canais ou regiões específicas?"
        )

    perguntas.append(
        "Como a receita evolui ao longo do período analisado?"
    )

    # Máximo de 5 perguntas

    perguntas = perguntas[:5]

    perguntas_text = "\n".join(
        f"- {pergunta}"
        for pergunta in perguntas
    )

    # ---------------------------------------------------------
    # Resultado
    # ---------------------------------------------------------

    return f"""
### Principais achados

{principais_achados_text}

### Oportunidades

{oportunidades_text}

### Pontos de atenção

{pontos_atencao_text}

### Próximas perguntas para investigação

{perguntas_text}
"""


# ---------------------------------------------------------
# Resumo com IA
# ---------------------------------------------------------

def generate_executive_summary(df=None) -> str:
    """
    Tenta gerar o resumo usando OpenAI.

    Caso a API não esteja configurada ou apresente algum erro,
    utiliza automaticamente a análise local.
    """

    if df is None:
        df = load_data()

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    # ---------------------------------------------------------
    # Sem configuração da API
    # ---------------------------------------------------------

    if not api_key or not model:
        return generate_local_summary(df)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""
Você é um analista de dados responsável por produzir um resumo
executivo para gestores.

Analise SOMENTE os dados fornecidos no contexto.

O contexto representa exatamente os filtros selecionados pelo usuário
no dashboard.

Sua resposta deve ser:

- objetiva;
- profissional;
- orientada a negócio;
- baseada exclusivamente nos dados disponíveis;
- escrita em português do Brasil.

REGRAS IMPORTANTES:

- Não invente métricas.
- Não crie números que não estejam no contexto.
- Não faça suposições sem evidência.
- Não apresente relações de causa e efeito sem dados.
- Não repita informações desnecessariamente.
- Não diga que um canal ou região é "líder" quando existir apenas
  um canal ou região no escopo.
- Quando houver apenas um canal ou região, deixe claro que o filtro
  selecionado contém apenas aquela categoria.
- Não sugira oportunidades genéricas.
- Priorize comparações, concentrações e diferenças que possam ser
  observadas diretamente nos dados.

Estruture EXATAMENTE nestas quatro seções:

### Principais achados

Apresente os resultados mais importantes do escopo, incluindo:

- receita;
- pedidos;
- ticket médio;
- principais destaques de canal, região e produto.

### Oportunidades

Identifique oportunidades baseadas diretamente nos dados.

Quando houver mais de um canal ou região, destaque diferenças relevantes.

Quando houver concentração relevante em um produto, destaque essa
informação de forma objetiva.

### Pontos de atenção

Informe:

- quantidade de anomalias;
- percentual dos registros;
- receita associada às anomalias.

Quando possível, destaque concentrações relevantes que mereçam
investigação.

### Próximas perguntas para investigação

Faça de 3 a 5 perguntas objetivas relacionadas aos dados disponíveis.

CONTEXTO DOS DADOS:

{build_context(df)}
"""

        response = client.responses.create(
            model=model,
            input=prompt,
        )

        return response.output_text

    except Exception:
        # A aplicação continua funcionando mesmo se a API
        # estiver sem crédito, indisponível ou apresentar erro.
        return generate_local_summary(df)


# ---------------------------------------------------------
# Teste local
# ---------------------------------------------------------

if __name__ == "__main__":
    print(generate_executive_summary())