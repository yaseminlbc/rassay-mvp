from app.database import engine, Base
import app.models

def reset_database():
    print("🧹 Eski ve bozuk tablolar temizleniyor...")
    Base.metadata.drop_all(bind=engine)
    
    print("✨ Yepyeni ve hatasız tablolar oluşturuluyor...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Veritabanı başarıyla sıfırlandı! Şimdi seed.py dosyasını çalıştırabilirsin.")

if __name__ == "__main__":
    reset_database()
    