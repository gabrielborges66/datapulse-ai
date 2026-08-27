from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sales.csv"
DB_PATH = ROOT / "data" / "sales.db"
REPORTS_PATH = ROOT / "reports"
REPORTS_PATH.mkdir(exist_ok=True)
