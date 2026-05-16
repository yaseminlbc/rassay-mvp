import pandas as pd
from app.database import engine

def upload_from_excel():
    # 1. Dosya adının doğruluğundan emin ol
    file_path = 'rassay_final_fixed.xlsx' 
    
    print(f"{file_path} okunuyor...")
    # Excel dosyasını oku
    df = pd.read_excel(file_path)

    # 2. Veri Temizliği (Önlem amaçlı)
    # Eğer Excel'de hala boş kalan yerler varsa onları 0 ile doldurur
    df = df.fillna(0)

    # 3. Veritabanına Aktar
    print(f"{len(df)} kayıt customers tablosuna aktarılıyor...")
    
    try:
        # 'to_sql' fonksiyonu binlerce satırı saniyeler içinde yükler
        # if_exists='append' sayesinde mevcut verilerin üzerine ekleme yapar
        df.to_sql('customers', con=engine, if_exists='append', index=False)
        print("Entegrasyon başarıyla tamamlandı!")
    except Exception as e:
        print(f"Hata oluştu: {e}")
        print("Not: Eğer 'UniqueViolation' hatası alıyorsan, veritabanındaki mevcut kayıtlarla CSV'deki company_id'ler çakışıyor olabilir.")

if __name__ == "__main__":
    upload_from_excel()