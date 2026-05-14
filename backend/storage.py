import pandas as pd
from datetime import datetime
import os


def get_user_sessions_file(username):
    """Kullanıcının oturum dosyası yolunu döndür"""
    os.makedirs("data", exist_ok=True)
    return f"data/sessions_{username}.csv"


def save_session(username, work_min, break_min, task, sentiment, focus_score):
    # 1. Klasör kontrolü
    if not os.path.exists("data"):
        os.makedirs("data")

    file_path = f"data/{username}_sessions.csv"

    # 2. Veri Hazırlama
    new_data = {
        "Tarih": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Calisma_Suresi": [work_min],
        "Mola_Suresi": [break_min],
        "Gorev": [task],
        "Duygu": [sentiment],
        "Odak_Puani": [focus_score],
    }

    new_df = pd.DataFrame(new_data)

    # 3. Dosyaya Yazma
    if os.path.exists(file_path):
        # Dosya varsa üstüne ekle (header=False)
        new_df.to_csv(file_path, mode="a", header=False, index=False)
    else:
        # Dosya yoksa yeni oluştur (header=True)
        new_df.to_csv(file_path, index=False)

def load_user_sessions(username):
    file_path = f"data/{username}_sessions.csv"
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Tarih sütununu düzelt
            df["Tarih"] = pd.to_datetime(df["Tarih"], errors='coerce')
            return df
        else:
            # Dosya yoksa boş şablon dön
            return pd.DataFrame(columns=["Tarih", "Calisma_Suresi", "Mola_Suresi", "Gorev", "Duygu", "Odak_Puani"])
    except Exception as e:
        print(f"Hata: {e}")
        return pd.DataFrame(columns=["Tarih", "Calisma_Suresi", "Mola_Suresi", "Gorev", "Duygu", "Odak_Puani"])


def get_daily_stats(username, days=30):
    df = load_user_sessions(username)
    if df.empty:
        return pd.DataFrame()

    # KRİTİK DÜZELTME: Önce sütunu datetime objesine çeviriyoruz
    # errors='coerce' parametresi, hatalı formatlı satırları boş geçerek çökmemesini sağlar.
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors="coerce")

    # Boş kalan satırlar varsa onları temizle
    df = df.dropna(subset=["Tarih"])

    # Şimdi .dt accessor'ını güvenle kullanabilirsin
    df["Tarih_Gun"] = df["Tarih"].dt.date

    daily_stats = df.groupby("Tarih_Gun").size().reset_index(name="Pomodoro_Sayisi")

    # Sütun ismini tekrar 'Tarih' yapalım ki grafikler kolay okusun
    daily_stats = daily_stats.rename(columns={"Tarih_Gun": "Tarih"})

    return daily_stats.tail(days)


def get_weekly_stats(username, weeks=12):
    df = load_user_sessions(username)
    if df.empty:
        return pd.DataFrame()

    # Aynı dönüşümü buraya da ekliyoruz
    df["Tarih"] = pd.to_datetime(df["Tarih"], errors="coerce")
    df = df.dropna(subset=["Tarih"])

    # Haftalık gruplandırma
    df["Hafta"] = df["Tarih"].dt.to_period("W").dt.start_time
    weekly_stats = df.groupby("Hafta").size().reset_index(name="Pomodoro_Sayisi")
    return weekly_stats.tail(weeks)
