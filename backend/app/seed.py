from app.database import SessionLocal
from app.models import Customer 

def seed_db():
    db = SessionLocal()
    try:
        test_customer = Customer(
            # DÜZELTME BURADA: "CUST-001" yerine sadece sayı olan 1 yazdık
            company_id=1, 
            mrr_value=2500.0,
            plan_type="Pro",
            account_age_months=18,
            support_tickets=1,
            login_count=120,
            churn_status=0,
            churn_probability=0.05
            # Eğer models.py'da company_name zorunluysa, buraya company_name="Test Şirketi" de ekleyebilirsin.
        )
        db.add(test_customer)
        db.commit()
        print("Müşteri verisi 'customers' tablosuna başarıyla eklendi!")
    except Exception as e:
        print(f"Hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
    