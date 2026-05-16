import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from app.database import engine

def test_model_performance():
    print("1. Veritabanından veriler çekiliyor...")
    df = pd.read_sql("SELECT * FROM customers", engine)
    
    print("2. Özellik Mühendisliği (Feature Engineering) yapılıyor...")
    # Sadece toplam sayılara değil, müşterinin "hızına" ve "trendine" bakıyoruz
    # +1 eklememizin sebebi, hesabı henüz 0 aylık olanlarda "Sıfıra Bölünme (ZeroDivision)" hatası almamak
    df['logins_per_month'] = df['login_count'] / (df['account_age_months'] + 1)
    df['tickets_per_month'] = df['support_tickets'] / (df['account_age_months'] + 1)
    
    # Modelin kullandığı özellikleri genişlettik (4'ten 6'ya çıktı)
    features = ['mrr_value', 'account_age_months', 'support_tickets', 'login_count', 'logins_per_month', 'tickets_per_month']
    X = df[features]
    y = df['churn_status']

    print("3. Veri %80 Eğitim (Train) ve %20 Test olarak bölünüyor...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    print("4. XGBoost Modeli (Yeni Özelliklerle) eğitiliyor...")
    # Hem Accuracy hem de Precision hedefini vurmak için ayarları dengeledik
    model = xgb.XGBClassifier(
        objective='binary:logistic', 
        random_state=42,
        max_depth=6,                      
        learning_rate=0.1,               
        n_estimators=250,                 
        subsample=0.9,                    
        colsample_bytree=0.9              
    )
    model.fit(X_train, y_train)

    print("5. Model test verisi üzerinde sınanıyor...\n")
    y_pred = model.predict(X_test)

    print("="*50)
    print(" 🚀 RASSAY XGBOOST MODEL BAŞARI RAPORU ")
    print("="*50)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Genel Doğruluk Oranı (Accuracy): %{accuracy * 100:.2f}")
    
    if accuracy >= 0.85:
        print("✅ NFR-ST-01 Kuralı BAŞARIYLA SAĞLANDI! (Hedef: %85+)")
    else:
        print("⚠️ NFR-ST-01 Kuralı SAĞLANAMADI. Modelin iyileştirilmesi gerekiyor.")
    
    print("-" * 50)
    print("Detaylı Sınıflandırma Raporu (F1-Score / Recall / Precision):")
    print(classification_report(y_test, y_pred, target_names=['Kalıcı (0)', 'Churn (1)']))
    print("="*50)

if __name__ == "__main__":
    test_model_performance()
    