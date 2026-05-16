import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# .env dosyasındaki bilgileri okuyoruz
load_dotenv()

# Bağlantı adresini alıyoruz
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Engine oluşturuyoruz (Veritabanı ile köprüyü kuran kısım)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Veritabanı işlemleri (oturum) için sınıf
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modellerimizi (tabloları) türeteceğimiz temel sınıf
Base = declarative_base()

# Her API isteğinde veritabanı bağlantısı açıp kapatacak fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()