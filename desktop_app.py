"""
WorkBee Focus - Desktop Application Launcher
Bu script, Streamlit uygulamasını masaüstü uygulaması olarak çalıştırır.
"""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

# PyWebView için urllib
try:
    import urllib.request
except ImportError:
    pass

# PyWebView kullanarak native window
try:
    import webview
    USE_WEBVIEW = True
except ImportError:
    USE_WEBVIEW = False
    import webbrowser

def run_streamlit():
    """Streamlit uygulamasını başlat"""
    app_path = Path(__file__).parent / "app.py"
    
    # Streamlit komutunu arka planda çalıştır
    process = subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless",
        "true",
        "--server.port",
        "8501",
        "--browser.gatherUsageStats",
        "false",
        "--server.enableCORS",
        "false",
        "--server.enableXsrfProtection",
        "false"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return process

def check_server_ready(url="http://localhost:8501", max_wait=10):
    """Streamlit sunucusunun hazır olup olmadığını kontrol et"""
    import urllib.request
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except:
            time.sleep(0.5)
    return False

def open_webview():
    """Native webview penceresi aç"""
    if USE_WEBVIEW:
        # Streamlit'in başlaması için bekle
        print("⏳ Streamlit sunucusu başlatılıyor...")
        if check_server_ready():
            print("✅ Sunucu hazır, pencere açılıyor...")
            webview.create_window(
                '🐝 WorkBee Focus',
                'http://localhost:8501',
                width=1200,
                height=800,
                resizable=True,
                min_size=(800, 600)
            )
            webview.start(debug=False)
        else:
            print("❌ Sunucu başlatılamadı, tarayıcıda açılıyor...")
            webbrowser.open("http://localhost:8501")
    else:
        # WebView yoksa normal tarayıcı kullan
        time.sleep(2)
        webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    print("🐝 WorkBee Focus başlatılıyor...")
    
    if USE_WEBVIEW:
        print("📱 Native window modunda çalışıyor...")
    else:
        print("🌐 Tarayıcı modunda çalışıyor (pywebview kurulu değil)")
        print("💡 Daha iyi deneyim için: pip install pywebview")
    
    # Streamlit'i başlat
    try:
        streamlit_process = run_streamlit()
        
        if USE_WEBVIEW:
            # WebView ana thread'de çalışmalı
            open_webview()
            # WebView kapandığında Streamlit'i kapat
            streamlit_process.terminate()
        else:
            # Tarayıcıyı aç ve Streamlit'i bekle
            browser_thread = threading.Thread(target=open_webview, daemon=True)
            browser_thread.start()
            streamlit_process.wait()
            
    except KeyboardInterrupt:
        print("\n👋 WorkBee Focus kapatılıyor...")
        if 'streamlit_process' in locals():
            streamlit_process.terminate()
        sys.exit(0)

