
import PyInstaller.__main__
import sys
import os

def build():
    """Executable oluştur"""
    
    # PyInstaller parametreleri
    params = [
        "desktop_app.py",  # Ana script
        "--name=WorkBeeFocus",  # Executable adı
        "--onefile",  # Tek dosya olarak
        "--windowed",  # Konsol penceresi gizle (Windows için)
        "--icon=NONE",  # İkon eklemek isterseniz dosya yolu verin
        "--add-data=backend;backend",  # Backend klasörünü ekle
        "--add-data=data;data",  # Data klasörünü ekle (eğer varsa)
        "--hidden-import=streamlit",
        "--hidden-import=pandas",
        "--hidden-import=textblob",
        "--hidden-import=backend",
        "--hidden-import=backend.nlp",
        "--hidden-import=backend.scoring",
        "--hidden-import=backend.storage",
        "--hidden-import=backend.user_manager",
        "--hidden-import=webview",
        "--collect-all=streamlit",  # Streamlit'in tüm bağımlılıklarını topla
        "--collect-all=webview",  # WebView'in tüm bağımlılıklarını topla
        "--clean",  # Önceki build'leri temizle
    ]
    
    # macOS için windowed parametresi farklı
    if sys.platform == "darwin":
        params.remove("--windowed")
        params.append("--windowed")  # macOS'ta da çalışır
    
    PyInstaller.__main__.run(params)
    print("✅ Build tamamlandı! dist/ klasöründe WorkBeeFocus.exe dosyasını bulabilirsiniz.")

if __name__ == "__main__":
    print("🔨 WorkBee Focus masaüstü uygulaması build ediliyor...")
    build()

