import pandas as pd
import xgboost as xgb
import shap
from app.database import engine, SessionLocal
from app.models import XAIFactor, ChurnPrediction

def analyze_and_save_xai():
    print("1. Veriler çekiliyor ve model hazırlanıyor...")
    df = pd.read_sql("SELECT * FROM customers", engine)
    
    features = ['mrr_value', 'account_age_months', 'support_tickets', 'login_count']
    X = df[features]
    y = df['churn_status']

    model = xgb.XGBClassifier(objective='binary:logistic', random_state=42)
    model.fit(X, y)
    
    churn_probabilities = model.predict_proba(X)[:, 1]

    print("2. SHAP değerleri hesaplanıyor...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    print("3. Tahminler ve XAI verileri veritabanına kaydediliyor...")
    db = SessionLocal()
    
    try:
        # Önceki verileri temizle
        db.query(XAIFactor).delete()
        
        for index in range(len(df)):
            
            # Sayısal ID'yi kullanıyoruz
            cust_id_int = int(df.iloc[index]['id']) 
            prob_score = float(churn_probabilities[index])
            
            # ADIM A: churn_predictions'a yaz
            prediction_record = db.query(ChurnPrediction).filter(ChurnPrediction.company_id == cust_id_int).first()
            
            if not prediction_record:
                 prediction_record = ChurnPrediction(
                     company_id=cust_id_int,
                     risk_score=prob_score,
                     model_version="v1.0-xgboost" 
                 )
                 db.add(prediction_record)
                 db.flush() 
            else:
                 prediction_record.risk_score = prob_score
                 prediction_record.model_version = "v1.0-xgboost"
                 db.flush()
                 
            current_prediction_id = prediction_record.prediction_id

            # ADIM B: xai_factors'a yaz
            for feature_idx, feature in enumerate(features):
                impact = float(shap_values[index][feature_idx])
                
                if abs(impact) > 0.01:
                    dir_val = "Pozitif" if impact > 0 else "Negatif"
                    
                    if abs(impact) > 0.5:
                        level = "Yüksek"
                    elif abs(impact) > 0.2:
                        level = "Orta"
                    else:
                        level = "Düşük"

                    new_xai_record = XAIFactor(
                        prediction_id=current_prediction_id,
                        feature_name=feature,
                        impact_value=impact,
                        impact_level=level,
                        direction=dir_val
                    )
                    db.add(new_xai_record)
        
        db.commit()
        print("Harika! Tahminler ve SHAP değerleri başarıyla veritabanına yazıldı.")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    analyze_and_save_xai()


