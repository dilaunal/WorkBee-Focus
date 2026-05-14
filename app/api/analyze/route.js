import clientPromise from '@/lib/mongodb';
import { ObjectId } from 'mongodb';

export async function POST(request) {
  try {
    // MongoDB bağlantısını kuruyoruz
    const client = await clientPromise;
    const db = client.db('workbee');
    
    // İstekten gelen veriyi alıyoruz
    const body = await request.json();
    const { feedbackText, userId, calisma_suresi, mola_suresi } = body;

    // Basit bir duygu analizi/puanlama mantığı (NLP simülasyonu)
    let focusScore = 70; // Varsayılan temel odak puanı
    let duyguDurumu = "Nötr";

    // TextBlob benzeri mantık için basit bir kelime kontrolü veya analiz
    if (feedbackText) {
      const lowerText = feedbackText.toLowerCase();
      if (lowerText.includes("kolay") || lowerText.includes("iyi") || lowerText.includes("odaklandım")) {
        focusScore = 85;
        duyguDurumu = "Olumlu";
      } else if (lowerText.includes("zor") || lowerText.includes("dağıldım") || lowerText.includes("yorgun")) {
        focusScore = 50;
        duyguDurumu = "Olumsuz";
      }
    }

    const sessionData = {
      userId,
      tarih: new Date(),
      calisma_suresi,
      mola_suresi,
      geri_bildirim: feedbackText,
      duygu: duyguDurumu,
      odak_puani: focusScore
    };

    // Veriyi MongoDB'ye kaydediyoruz
    const result = await db.collection('focus_sessions').insertOne(sessionData);

    return new Response(JSON.stringify({ 
      success: true, 
      data: {
        odak_puani: focusScore,
        duygu: duyguDurumu,
        message: "Seans başarıyla analiz edildi ve kaydedildi."
      } 
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (error) {
    return new Response(JSON.stringify({ success: false, error: 'Analiz işlemi başarısız oldu.' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}