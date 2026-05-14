# WorkBee Focus - Masaüstü Uygulaması

Bu uygulama, Streamlit tabanlı WorkBee Focus uygulamasını masaüstü uygulaması olarak çalıştırır.

## Özellikler

- ✅ Native masaüstü penceresi (PyWebView ile)
- ✅ Tarayıcıya gerek kalmadan çalışır
- ✅ Tek tıkla başlatma
- ✅ Executable oluşturma desteği (PyInstaller)

## Kurulum

### Adım 1: Gerekli Paketleri Kurun

```bash
pip install -r requirements_desktop.txt
```

**Not:** PyWebView kurulumu platforma göre değişir:
- **Windows:** Otomatik kurulur
- **macOS:** `pip install pywebview` yeterli
- **Linux:** Sistem paketleri gerekebilir (libwebkit2gtk veya webkitgtk)

### Adım 2: Uygulamayı Çalıştırın

#### Python ile:
```bash
python desktop_app.py
```

#### Windows'ta (.bat dosyası ile):
```bash
run_desktop.bat
```

Uygulama otomatik olarak:
1. Streamlit sunucusunu başlatır (localhost:8501)
2. Native bir pencere açar (PyWebView varsa) veya tarayıcıda açar

## Kullanım Modları

### 1. Native Window Modu (Önerilen)
PyWebView kurulu ise, uygulama native bir masaüstü penceresi olarak açılır.
- Daha iyi kullanıcı deneyimi
- Tarayıcıya gerek yok
- Native görünüm

### 2. Tarayıcı Modu
PyWebView kurulu değilse, uygulama varsayılan tarayıcıda açılır.
- Daha basit kurulum
- Tüm özellikler çalışır

## Executable Oluşturma

1. PyInstaller'ı kurun (zaten requirements_desktop.txt'de var):
```bash
pip install pyinstaller
```

2. Build script'ini çalıştırın:
```bash
python build_desktop.py
```

3. Oluşturulan executable'ı bulun:
   - Windows: `dist/WorkBeeFocus.exe`
   - macOS: `dist/WorkBeeFocus`
   - Linux: `dist/WorkBeeFocus`

**Not:** Executable oluştururken tüm bağımlılıklar dahil edilir, bu yüzden dosya boyutu büyük olabilir (100-200MB).

## Notlar

- Uygulama `http://localhost:8501` adresinde çalışır
- Veriler `data/` klasöründe saklanır
- İlk çalıştırmada 2-3 saniye bekleyin (sunucu başlatılıyor)
- Pencereyi kapatmak Streamlit sunucusunu da kapatır

## Sorun Giderme

- **Modül bulunamadı hatası:** `--hidden-import` parametrelerini kontrol edin
- **Windows'ta antivirüs engellemesi:** Executable'ı güvenilir olarak işaretleyin
- **PyWebView çalışmıyor:** Tarayıcı modunda da çalışır, sorun değil
- **Linux'ta WebView hatası:** Sistem paketlerini kurun: `sudo apt-get install python3-webkit` veya `sudo apt-get install python3-webkit2`
