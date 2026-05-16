"""
seed.py — Import real customer data from rassay_final_fixed.xlsx into PostgreSQL.

Behaviour:
  - Clears existing rows from customers, churn_predictions, xai_factors,
    alerts, and usage_data before inserting, so re-running is always safe.
  - Uses bulk_insert_mappings for speed (7 000+ rows in a single round-trip).
  - Resolves the Excel path relative to this file, so it works regardless of
    the working directory you run the script from.

Run from backend/:
    python -m app.seed
  or:
    python app/seed.py
"""

from pathlib import Path
import sys
import pandas as pd
from sqlalchemy import text

from app.database import SessionLocal, engine, Base
import app.models as models   # ensure all tables are registered

EXCEL_PATH = Path(__file__).parent.parent / "rassay_final_fixed.xlsx"

CLEAR_ORDER = [
    "xai_factors",
    "churn_predictions",
    "alerts",
    "usage_data",
    "customers",
]


def _clear_tables(db):
    print("Clearing existing data...")
    for table in CLEAR_ORDER:
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()
    print(f"  Cleared {len(CLEAR_ORDER)} tables.")


def _load_excel() -> pd.DataFrame:
    if not EXCEL_PATH.exists():
        print(f"ERROR: Excel file not found at {EXCEL_PATH}")
        sys.exit(1)

    print(f"Reading {EXCEL_PATH.name} ...")
    df = pd.read_excel(EXCEL_PATH, dtype={"company_id": str})

    required = {"company_id", "mrr_value", "plan_type",
                "account_age_months", "support_tickets", "login_count", "churn_status"}
    missing = required - set(df.columns)
    if missing:
        print(f"ERROR: Excel is missing columns: {missing}")
        sys.exit(1)

    # Drop any rows where critical fields are null
    before = len(df)
    df = df.dropna(subset=list(required))
    dropped = before - len(df)
    if dropped:
        print(f"  Dropped {dropped} rows with null values.")

    print(f"  Loaded {len(df):,} customer records.")
    return df


def seed_db():
    Base.metadata.create_all(bind=engine)  # ensure tables exist

    df = _load_excel()

    db = SessionLocal()
    try:
        _clear_tables(db)

        print("Inserting customers...")
        records = [
            {
                "company_id":          str(row.company_id).strip(),
                "mrr_value":           float(row.mrr_value),
                "plan_type":           str(row.plan_type).strip(),
                "account_age_months":  int(row.account_age_months),
                "support_tickets":     int(row.support_tickets),
                "login_count":         int(row.login_count),
                "churn_status":        int(row.churn_status),
                "churn_probability":   None,
            }
            for row in df.itertuples(index=False)
        ]

        db.bulk_insert_mappings(models.Customer, records)
        db.commit()

        total = db.query(models.Customer).count()
        churned = db.query(models.Customer).filter(models.Customer.churn_status == 1).count()
        print(f"\nDone.")
        print(f"  Total customers inserted : {total:,}")
        print(f"  Churned (label=1)        : {churned:,}")
        print(f"  Retained (label=0)       : {total - churned:,}")

    except Exception as exc:
        print(f"\nERROR during seed: {exc}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
