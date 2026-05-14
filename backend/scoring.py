from datetime import datetime

def calculate_focus_score(sentiment, work_duration):
    # Başlangıç puanı
    base_score = 70
    
    # 1. Duygu Durumu Etkisi (NLP'den gelen veri)
    sentiment_bonus = {
        "Pozitif": 15,
        "Nötr": 5,
        "Negatif": -10
    }
    
    # 2. Seans Uzunluğu Etkisi (İdeal odak süresi 25-45 dk arasıdır)
    if 25 <= work_duration <= 45:
        duration_bonus = 10
    else:
        duration_bonus = 0 # Çok kısa veya çok uzun seanslarda bonus yok
        
    # 3. Saat Dilimi Etkisi (Biyolojik saat: Sabah verimi)
    current_hour = datetime.now().hour
    if 8 <= current_hour <= 12:
        hour_bonus = 5  # Altın saatler
    elif current_hour >= 22:
        hour_bonus = -5 # Geç saatlerde odak düşer
    else:
        hour_bonus = 0

    # Final Puanı Hesapla
    final_score = base_score + sentiment_bonus.get(sentiment, 0) + duration_bonus + hour_bonus
    
    # Puanı 0-100 arasında sınırla
    return max(0, min(100, final_score))