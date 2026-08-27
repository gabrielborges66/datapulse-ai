import os
from dotenv import load_dotenv

from .analysis import load_data, calculate_kpis, detect_anomalies

load_dotenv()

def build_context() -> str:
    df = load_data()
    kpis = calculate_kpis(df)
    anomalies = detect_anomalies(df).head(5)

    by_channel = (
        df.groupby("channel")["revenue"]
          .sum()
          .sort_values(ascending=False)
    )
    by_region = (
        df.groupby("region")["revenue"]
          .sum()
          .sort_values(ascending=False)
    )

    return f"""
KPIs:
- Receita: R$ {kpis["revenue"]:.2f}
- Pedidos: {kpis["orders"]}
- Ticket médio: R$ {kpis["average_ticket"]:.2f}
- Margem: {kpis["margin_rate"]:.2f}%

Canal líder: {by_channel.index[0]} (R$ {by_channel.iloc[0]:.2f})
Região líder: {by_region.index[0]} (R$ {by_region.iloc[0]:.2f})
Anomalias identificadas: {len(detect_anomalies(df))}

Principais anomalias:
{anomalies[["order_id", "date", "channel", "product", "revenue"]].to_string(index=False)}
"""

def generate_executive_summary():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key or not model:
        return (
            "IA não configurada. Configure OPENAI_API_KEY e OPENAI_MODEL "
            "para gerar o resumo executivo."
        )

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    prompt = f"""
Você é um analista de dados. Gere um resumo executivo curto, objetivo e
orientado a negócio usando SOMENTE os dados abaixo.

Contexto:
{build_context()}

Estruture em:
1. Principais achados
2. Oportunidades
3. Pontos de atenção
4. Próximas perguntas para investigação

Não invente métricas.
"""

    response = client.responses.create(model=model, input=prompt)
    return response.output_text

if __name__ == "__main__":
    print(generate_executive_summary())
