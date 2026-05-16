import pandas as pd
import xgboost as xgb
import shap  # XAI faktörleri için ekledik
from datetime import datetime
from app.database import engine, SessionLocal
from app.models import Customer, ChurnPrediction, XAIFactor

def run_churn_pipeline():
    db = SessionLocal()
    print("1. Veritabanından veriler çekiliyor...")
    df = pd.read_sql("SELECT * FROM customers", engine)

    if df.empty:
        print("Hata: Veritabanında işlenecek müşteri bulunamadı.")
        return

    # 2. Veri Ön İşleme
    print("2. Veriler model için hazırlanıyor...")
    features = ['mrr_value', 'account_age_months', 'support_tickets', 'login_count']
    X = df[features]
    y = df['churn_status']

    # 3. Model Eğitimi
    print("3. XGBoost modeli eğitiliyor...")
    model = xgb.XGBClassifier(objective='binary:logistic', random_state=42)
    model.fit(X, y)

    # 4. XAI Analizi (SHAP değerleri hesaplanıyor)
    print("4. XAI: Karar mekanizması analiz ediliyor (SHAP)...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # 5. Sonuçları Profesyonel Tablolara Kaydetme
    print("5. Tahminler ve XAI faktörleri tablolara işleniyor...")
    try:
        # Önce bu çalıştırmadaki tüm tahminleri bir listeye alalım
        churn_probabilities = model.predict_proba(X)[:, 1]

        for i, row in df.iterrows():
            prob = float(churn_probabilities[i])
            
            # Risk seviyesini belirle
            risk_lvl = "Low"
            if prob > 0.7: risk_lvl = "High"
            elif prob > 0.4: risk_lvl = "Medium"

            # A. ChurnPrediction tablosuna kayıt
            new_prediction = ChurnPrediction(
                company_id=str(row['company_id']), # String tipine dikkat
                risk_score=prob,
                risk_level=risk_lvl,
                calculation_date=datetime.now(),
                model_version="v1.0-xgboost"
            )
            db.add(new_prediction)
            db.flush()  # prediction_id'yi almak için veritabanına fısıldıyoruz

            # B. XAI Factors tablosuna en etkili 2 faktörü kaydetme
            # SHAP değerlerine bakarak o satır için en önemli özellikleri buluyoruz
            feature_impacts = dict(zip(features, shap_values[i]))
            # En yüksek etkili 2 özelliği seç
            top_features = sorted(feature_impacts.items(), key=lambda x: abs(x[1]), reverse=True)[:2]

            for f_name, f_impact in top_features:
                xai_entry = XAIFactor(
                    prediction_id=new_prediction.prediction_id,
                    feature_name=f_name,
                    impact_value=float(f_impact),
                    impact_level="High" if abs(f_impact) > 0.5 else "Medium"
                )
                db.add(xai_entry)

        db.commit()
        print(f"🚀 Başarılı! {len(df)} müşteri için tahminler ve XAI analizleri kaydedildi.")

    except Exception as e:
        print(f"Kayıt sırasında hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_churn_pipeline()
    