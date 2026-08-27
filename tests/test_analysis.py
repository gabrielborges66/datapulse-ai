import pandas as pd
from src.analysis import calculate_kpis, detect_anomalies

def test_kpis():
    df = pd.DataFrame({
        "order_id": [1, 2],
        "revenue": [100.0, 200.0],
        "margin": [40.0, 80.0],
    })
    result = calculate_kpis(df)
    assert result["revenue"] == 300.0
    assert result["orders"] == 2
    assert result["average_ticket"] == 150.0
    assert result["margin"] == 120.0

def test_anomaly_detection():
    df = pd.DataFrame({"revenue": [10, 11, 12, 13, 14, 1000]})
    anomalies = detect_anomalies(df)
    assert 1000 in anomalies["revenue"].tolist()
