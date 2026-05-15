import streamlit as st
import time
import pandas as pd
import os
from datetime import datetime, timedelta
import datetime as dt  # Tarih işlemleri için çakışmayı önleyici takma ad
from textBlob_import_helper import TextBlob # Kütüphanelerin çakışmasını engellemek için
from backend.nlp import analyze_sentiment
from backend.scoring import calculate_focus_score
from backend.storage import (
    save_session,
    load_user_sessions,
    get_daily_stats,
    get_weekly_stats,
)
from backend.user_manager import register_user, login_user
import random
from pymongo import MongoClient
import urllib.parse

# 1. Sayfa Yapılandırması (Tarayıcı sekmesi için)
st.set_page_config(
    page_title="WorkBee Focus",
    page_icon="WorkBeeAppIcon.png",
    layout="wide"
)

# 2. Mobil (iOS/Safari) İkon Zorlaması ve PWA Manifesti
st.markdown(
    """
    <link rel="apple-touch-icon" href="./WorkBeeAppIcon.png?v=2">
    <link rel="manifest" href="./manifest.json?v=2">
    """,
    unsafe_allow_html=True
)


# MongoDB Bağlantı Kurulumu - GÜVENLİ YÖNTEM
@st.cache_resource
def init_connection():
    # Şifreyi kodun içinden değil, Streamlit'in güvenli kasasından çekiyoruz
    mongo_uri = st.secrets["mongo"]["connection_string"]
    return MongoClient(mongo_uri)

client = init_connection()
db = client['workbee'] # Veritabanı adı

try:
    client.admin.command('ping')
except Exception as e:
    st.error(f"Bağlantı hatası: {e}")


# --- 2. FONKSİYONLAR ---
def analiz_et_ve_kaydet(feedback_text, calisma_suresi, mola_suresi):
    focus_score = 70
    duygu_durumu = "Nötr"
    
    if feedback_text:
        text_lower = feedback_text.lower()
        if any(word in text_lower for word in ["kolay", "iyi", "odaklandım", "harika"]):
            focus_score = 85
            duygu_durumu = "Olumlu"
        elif any(word in text_lower for word in ["zor", "dağıldım", "yorgun", "kötü"]):
            focus_score = 50
            duygu_durumu = "Olumsuz"
            
    session_data = {
        "tarih": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "calisma_suresi": calisma_suresi,
        "mola_suresi": mola_suresi,
        "geri_bildirim": feedback_text,
        "duygu": duygu_durumu,
        "odak_puani": focus_score
    }
    
    db.focus_sessions.insert_one(session_data)
    return focus_score, duygu_durumu


def get_advanced_bee_coach_advice(
    sentiment, focus_score, work_min, total_pomo, tasks_left
):
    intros = [
        "Selam Bal Arısı!",
        "Kovanın analizi hazır!",
        "Arı Koç konuşuyor:",
        "Bee-Analiz tamamlandı:",
    ]

    if focus_score > 80:
        focus_msg = "🎯 Odaklanman muazzam, tam bir 'Deep Work' (Derin Çalışma) halindesin."
    elif focus_score > 50:
        focus_msg = "⚖️ Dengen iyi ancak ufak dikkat dağıtıcılar seni biraz yavaşlatmış olabilir."
    else:
        focus_msg = "🌫️ Zihnin bugün biraz puslu gibi, odaklanmakta zorlanıyorsun. Kısa bir yürüyüşe ne dersin?"

    if sentiment == "Negatif":
        advice = f"Moralin biraz düşük görünüyor ama unutma; bugüne kadar **{total_pomo} seans** bitirdin! Bu disiplin seni başarıya götürecek."
    elif work_min > 45:
        advice = "Seans süren oldukça uzun. Beynin yorulmuş olabilir, bir sonraki molanı mutlaka uzun tut."
    else:
        advice = "Harika bir tempo tutturmuşsun, istikrarın kovanı geliştirmeye devam ediyor."

    if tasks_left == 0:
        task_msg = "Tüm görevlerini tamamlamışsın! Kovanın en çalışkan arısı sensin. 🎊"
    else:
        task_msg = f"Hala yapman gereken **{tasks_left} görev** var. Adım adım ilerle, hepsini bitirebilirsin!"

    tips = [
        "💡 İpucu: Çalışırken su içmek zihinsel berraklığını %14 oranında artırır.",
        "💡 İpucu: Beyin, 90 dakikadan sonra odaklanma yetisini kaybeder. Molaları sakın atlama!",
        "💡 İpucu: En zor işini sabah ilk seansta bitir (Ye O Kurbağayı tekniği).",
        "💡 İpucu: Çalışırken telefonu başka odaya bırakmak odağını ikiye katlar.",
    ]

    return f"""
    ### {random.choice(intros)}
    
    {focus_msg}
    
    {advice}
    
    {task_msg}
    
    ---
    *{random.choice(tips)}*
    """


# --- 3. CSS STİLLERİ ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
    }
    h1, h2, h3, p, span, label {
        color: #FFC107 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    div.stButton > button:first-child {
        background-color: #FFC107 !important;
        color: #000000 !important;
        border: 2px solid #FFC107;
        border-radius: 12px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);
    }
    div.stButton > button:hover {
        background-color: #FFD54F !important;
        box-shadow: 0 4px 25px rgba(255, 193, 7, 0.5);
        transform: scale(1.02);
    }
    .timer-container {
        border: 3px solid #FFC107;
        border-radius: 50%;
        padding: 50px;
        width: 300px;
        height: 300px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle, rgba(255,193,7,0.1) 0%, rgba(0,0,0,0) 70%);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1A1C23 !important;
        color: #FFC107 !important;
        border: 1px solid #FFC107 !important;
    }
    @keyframes vizz {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    .bee-icon {
        font-size: 50px;
        display: block;
        text-align: center;
        animation: vizz 2s infinite ease-in-out;
    }
    [data-testid="stSidebar"] {
        background-color: #FFC107 !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #FFC107 !important;
    }
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="slider"] > div {
        background-color: rgba(0,0,0,0.1) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="slider"] > div > div {
        background-color: #000000 !important;
    }
    [data-testid="stSidebar"] [role="slider"] {
        background-color: #000000 !important;
        border: 2px solid #FFC107 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: #000000 !important;
        color: #FFC107 !important;
        border: 1px solid #000000 !important;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #333333 !important;
        color: #FFC107 !important;
        transform: scale(1.02);
    }
    [data-testid="stSidebar"] hr {
        border-top: 2px solid #000000 !important;
    }
    .stTextInput>div>div>input {
        color: #FFFFFF !important;
        background-color: #1A1C23 !important;
        border: 1px solid #FFC107 !important;
    }
    .stTextInput>div>div>input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    .task-text {
        color: #FFFFFF !important;
        font-size: 1.1rem;
    }
    [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    del, s, strike {
        color: #888888 !important;
    }
    div[data-baseweb="input"] input {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    .stCheckbox label p {
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    div[data-baseweb="input"] input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    .stMarkdown p {
        color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- 4. VERİ YÖNETİMİ (SESSION STATE) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "total_pomo" not in st.session_state:
    st.session_state.total_pomo = 0


# --- 5. YAN PANEL (SIDEBAR) ---
with st.sidebar:
    st.markdown(
        """
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='font-size: 2.5rem; margin: 0;'>🐝</h1>
        <h2 style='color: #FFC107; margin: 10px 0;'>WorkBee Focus</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### ⚙️ Ayarlar")
    work_min = st.slider("⏱️ Çalışma Süresi (dakika)", 1, 60, 25)
    break_min = st.slider("☕ Mola Süresi (dakika)", 1, 30, 5)

    st.markdown("---")
    if st.session_state.logged_in and st.session_state.username:
        st.markdown(f"### 👤 {st.session_state.username}")
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.total_pomo = 0
            st.session_state.tasks = []
            st.rerun()

    st.markdown("---")
    if st.session_state.logged_in and st.session_state.username:
        st.markdown("### 📊 İstatistikler")
        user_df = load_user_sessions(st.session_state.username)
        total_user_pomo = len(user_df)

        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("🎯 Toplam Pomodoro", total_user_pomo)
        with col_stat2:
            completed_tasks = len([t for t in st.session_state.tasks if t["done"]])
            st.metric("✅ Tamamlanan Görev", completed_tasks)

    st.markdown("---")
    st.markdown("💡 **İpucu:** Düzenli molalar verimliliğini artırır!")

    st.header("Mobil Uygulama")
    pwa_install_script = """
    <script>
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        window.deferredPrompt = e;
    });

    function installApp() {
        const promptEvent = window.deferredPrompt;
        if (promptEvent) {
            promptEvent.prompt();
            promptEvent.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('Kullanıcı uygulamayı kurmayı kabul etti.');
                }
                window.deferredPrompt = null;
            });
        }
    }
    </script>
    <button onclick="installApp()" style="width: 100%; padding:10px; background-color:#fbbf24; color:#000; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
      📱 Cihaza Kur
    </button>
    """
    st.markdown(pwa_install_script, unsafe_allow_html=True)


# --- 6. KULLANICI GİRİŞ KONTROLÜ ---
if not st.session_state.logged_in:
    st.markdown(
        """
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%); 
                border-radius: 30px; margin: 40px auto; max-width: 500px;'>
        <h2>🐝 WorkBee Focus'a Hoş Geldin!</h2>
        <p>Devam etmek için giriş yap veya kayıt ol</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol"])

    with login_tab:
        st.markdown("### Giriş Yap")
        login_username = st.text_input("Kullanıcı Adı", key="login_username")
        login_password = st.text_input("Şifre", type="password", key="login_password")

        if st.button("Giriş Yap", use_container_width=True):
            if login_username and login_password:
                success, message = login_user(login_username, login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    df = load_user_sessions(login_username)
                    st.session_state.total_pomo = len(df)
                    st.success("✅ Giriş başarılı!")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Lütfen tüm alanları doldurun.")

    with register_tab:
        st.markdown("### Yeni Hesap Oluştur")
        reg_username = st.text_input("Kullanıcı Adı", key="reg_username")
        reg_password = st.text_input("Şifre", type="password", key="reg_password")
        reg_password2 = st.text_input("Şifre Tekrar", type="password", key="reg_password2")

        if st.button("Kayıt Ol", use_container_width=True):
            if reg_username and reg_password and reg_password2:
                if reg_password != reg_password2:
                    st.error("❌ Şifreler eşleşmiyor!")
                else:
                    success, message = register_user(reg_username, reg_password)
                    if success:
                        st.success(f"✅ {message}")
                        st.info("Şimdi giriş yapabilirsiniz!")
                    else:
                        st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Lütfen tüm alanları doldurun.")

    st.stop()


# --- 7. ANA EKRAN (TABS) ---
st.markdown(
    """
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='margin: 0;'>🐝 WorkBee FocusPomo</h1>
        <p style='color: #666; font-size: 1.1rem; margin-top: 10px;'>Odaklan, Çalış, Başar! 🚀</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(["🕒 Zamanlayıcı", "📝 Görevler", "🧠 AI Koç", "📊 İstatistikler"])

# --- TAB 1: ZAMANLAYICI ---
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    placeholder = st.empty()

    col1, col2, col3 = st.columns([0.1, 4, 0.1])
    with col2:
        placeholder.markdown(
            f"""
            <div style='text-align: center; padding: 40px; background: radial-gradient(circle, rgba(255,193,7,0.15) 0%, rgba(0,0,0,0.8) 100%); 
                        border: 6px solid #FFC107; border-radius: 60px; margin: 10px 0; box-shadow: 0 0 50px rgba(255,193,7,0.2);'>
                <h1 style='font-size: 300px !important; color: #FFC107 !important; font-weight: 900; margin: 0; line-height: 0.9; font-family: "Courier New", Courier, monospace;'>
                    {work_min:02d}:00
                </h1>
                <p style='color: #FFC107; letter-spacing: 15px; font-size: 1.5rem; opacity: 0.7;'>HAZIR MISIN?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 ODAKLANMAYI BAŞLAT", key="start_timer", use_container_width=True):
            total_sec = work_min * 60
            progress_bar = st.progress(0)
            status_text = st.empty()

            while total_sec > 0:
                mins, secs = divmod(total_sec, 60)
                placeholder.markdown(
                    f"""
                    <div style='text-align: center; padding: 40px; background: radial-gradient(circle, rgba(255,193,7,0.2) 0%, rgba(0,0,0,0.9) 100%); 
                                border: 6px solid #FFC107; border-radius: 60px; margin: 10px 0; box-shadow: 0 0 80px rgba(255,193,7,0.3);'>
                        <h1 style='font-size: 300px !important; color: #FFC107 !important; font-weight: 900; margin: 0; line-height: 0.9; font-family: "Courier New", Courier, monospace; text-shadow: 0 0 40px rgba(255,193,7,0.5);'>
                            {mins:02d}:{secs:02d}
                        </h1>
                        <p style='color: #FFC107; letter-spacing: 20px; font-size: 1.5rem; font-weight: bold;'>ODAKLAN</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                progress = (work_min * 60 - total_sec) / (work_min * 60)
                progress_bar.progress(progress)
                status_text.markdown(
                    f"<p style='text-align:center; color:#FFC107;'>🐝 Seansın bitmesine {mins} dakika {secs} saniye kaldı...</p>",
                    unsafe_allow_html=True,
                )
                time.sleep(1)
                total_sec -= 1

            st.markdown(
                """<audio autoplay><source src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3" type="audio/mpeg"></audio>""",
                unsafe_allow_html=True,
            )
            progress_bar.progress(1.0)
            status_text.empty()
            st.balloons()
            st.success("🎉 **Tebrikler! Seans başarıyla tamamlandı ve veritabanına işlendi.**")

            st.session_state.total_pomo += 1
            akilli_puan = calculate_focus_score("Nötr", work_min)

            try:
                save_session(
                    st.session_state.username,
                    work_min,
                    break_min,
                    "Odaklanma Seansı",
                    "Nötr",
                    akilli_puan,
                )
            except Exception as e:
                st.error(f"⚠️ Veri kaydedilirken hata oluştu: {e}")

            placeholder.markdown(
                f"""
                <div style='text-align: center; padding: 100px; background: #FFC107; border-radius: 60px; margin: 10px 0;'>
                    <h1 style='font-size: 150px !important; color: #000; font-weight: 900; margin: 0;'>MOLA!</h1>
                    <p style='color: #000; font-size: 2rem; font-weight: bold;'>Dinlenme zamanı, arı kardeş. 🐝</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

# --- TAB 2: GÖREVLER (TO-DO) ---
with tab2:
    st.markdown("<h2 style='color: #FFC107;'>📝 Görevlerim</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: white;'>Yapılacaklar listeni oluştur ve hedeflerine odaklan!</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("add_task_form", clear_on_submit=True):
        t_col1, t_col2 = st.columns([4, 1])
        with t_col1:
            new_task = st.text_input(
                "➕ Yeni görev ekle",
                placeholder="Örn: Proje ödevini tamamla...",
                key="new_task_input",
            )
        with t_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Ekle", use_container_width=True)

        if submitted and new_task.strip():
            st.session_state.tasks.append({"task": new_task.strip(), "done": False})
            st.success("✅ Görev eklendi!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.tasks:
        st.markdown("<h3 style='color: #FFC107;'>📌 Aktif Görevler</h3>", unsafe_allow_html=True)

        for i, task_obj in enumerate(st.session_state.tasks):
            with st.container():
                c1, c2, c3 = st.columns([0.1, 0.75, 0.15])
                done = c1.checkbox("", value=task_obj["done"], key=f"check_{i}")

                if done != task_obj["done"]:
                    st.session_state.tasks[i]["done"] = done
                    st.rerun()

                if done:
                    c2.markdown(
                        f"<div style='color: #888888; text-decoration: line-through; font-size: 1.2rem; padding-top: 5px;'>{task_obj['task']}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    c2.markdown(
                        f"<div style='color: #FFFFFF; font-size: 1.2rem; font-weight: 500; padding-top: 5px;'>{task_obj['task']}</div>",
                        unsafe_allow_html=True,
                    )

                if c3.button("🗑️", key=f"del_{i}"):
                    st.session_state.tasks.pop(i)
                    st.rerun()

                st.markdown("<hr style='border-top: 1px solid #333; margin: 5px 0;'>", unsafe_allow_html=True)
    else:
        st.info("📝 Henüz görev eklenmedi. Yukarıdaki formdan yeni görev ekleyebilirsin!")

# --- TAB 3: AI GERİ BİLDİRİM ---
with tab3:
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(255,193,7,0.1) 0%, rgba(0,0,0,0.5) 100%); 
                    border-radius: 20px; margin-bottom: 30px; border: 1px solid #FFC107;'>
            <h2 style='color: #FFC107;'>🤖 Akıllı Arı Koçu</h2>
            <p style='color: white;'>Durumunu analiz edip sana özel stratejiler belirleyeyim.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_note = st.text_area(
        "📝 Şu anki durumunu anlat:",
        placeholder="Örn: Çok zordu... veya Çok kolaydı, hemen bitti!",
        height=100,
    )

    if st.button("💡 Koçtan Tavsiye Al", use_container_width=True):
        if user_note:
            with st.spinner("🐝 Veriler analiz ediliyor..."):
                time.sleep(1)
                sentiment, _ = analyze_sentiment(user_note)
                focus_score = calculate_focus_score(sentiment, work_min)
                text_lower = user_note.lower()

                if "zor" in text_lower or "yapamadım" in text_lower or "sıkıldım" in text_lower:
                    advice_title = "💪 Pes Etme, Gelişiyorsun!"
                    advice_text = "Zorlanıyorsan öğreniyorsun demektir! Zihnini yormamak için bir sonraki seansı daha kısa tut veya görevi küçük parçalara böl."
                    box_type = "warning"
                elif "kolay" in text_lower or "basit" in text_lower or "hızlı" in text_lower:
                    advice_title = "🚀 Vites Yükseltme Zamanı!"
                    advice_text = "Harikasın! Bu konu sana kolay geliyorsa zihnin tam kapasite çalışıyor. Hazır ivme kazanmışken en zor görevini şimdi aradan çıkar!"
                    box_type = "success"
                elif "yorgun" in text_lower or "uyku" in text_lower:
                    advice_title = "😴 Mola Vermek de Çalışmaya Dahildir"
                    advice_text = "Yorgun bir zihinle çalışmak boşa kürek çekmektir. Hemen 10 dakikalık bir esneme veya yüz yıkama molası ver."
                    box_type = "info"
                elif sentiment == "Pozitif":
                    advice_title = "🌟 Harika Enerji!"
                    advice_text = "Pozitif bir moddasın! Bu enerjiyi odaklanmanı derinleştirmek için kullan."
                    box_type = "success"
                else:
                    advice_title = "🐝 Kovan İstikrar Bekler"
                    advice_text = "Dengeli bir gidişatın var. Pomodoro tekniğine sadık kalarak devam et."
                    box_type = "info"

                st.markdown("---")
                if box_type == "success":
                    st.success(f"**{advice_title}**\n\n{advice_text}")
                elif box_type == "warning":
                    st.warning(f"**{advice_title}**\n\n{advice_text}")
                else:
                    st.info(f"**{advice_title}**\n\n{advice_text}")

                st.metric("Tahmini Odak Skorun", f"{focus_score}/100 ⭐")

                save_session(
                    st.session_state.username,
                    work_min,
                    break_min,
                    user_note,
                    sentiment,
                    focus_score,
                )
        else:
            st.warning("⚠️ Lütfen durumunu anlatan bir not bırak.")

# --- TAB 4: İSTATİSTİKLER VE GRAFİKLER ---
with tab4:
    st.markdown("### 📊 Pomodoro İstatistiklerin")
    df = load_user_sessions(st.session_state.username)

    if df.empty:
        st.info("📊 Henüz pomodoro verisi yok. Seans tamamladıkça burada istatistiklerini görebilirsin!")
    else:
        if "Calisma_Suresi(dk)" in df.columns:
            df = df.rename(columns={"Calisma_Suresi(dk)": "Calisma_Suresi"})
        if "Odak_Skoru" in df.columns:
            df = df.rename(columns={"Odak_Skoru": "Odak_Puani"})

        df["Tarih"] = pd.to_datetime(df["Tarih"])

        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        total_pomos = len(df)
        total_work_time = df["Calisma_Suresi"].sum() if "Calisma_Suresi" in df.columns else 0
        avg_focus = df["Odak_Puani"].mean() if "Odak_Puani" in df.columns else 0
        total_days = (df["Tarih"].max() - df["Tarih"].min()).days + 1

        with col1:
            st.metric("🎯 Toplam Pomodoro", total_pomos)
        with col2:
            st.metric("⏱️ Toplam Çalışma", f"{int(total_work_time)} dk")
        with col3:
            st.metric("⭐ Ortalama Odak", f"{avg_focus:.1f}/100")
        with col4:
            st.metric("📅 Aktif Günler", total_days)

        st.markdown("---")
        chart_type = st.radio("Grafik Türü Seçin:", ["📅 Günlük Dağılım", "📆 Haftalık İlerleme"], horizontal=True)

        if chart_type == "📅 Günlük Dağılım":
            daily_df = get_daily_stats(st.session_state.username, days=30)
            if not daily_df.empty:
                daily_df["Tarih"] = pd.to_datetime(daily_df["Tarih"])
                st.line_chart(daily_df.set_index("Tarih")["Pomodoro_Sayisi"])
            else:
                st.info("Günlük veri henüz işlenmedi.")
        else:
            weekly_df = get_weekly_stats(st.session_state.username, weeks=12)
            if not weekly_df.empty:
                st.bar_chart(weekly_df.set_index("Hafta")["Pomodoro_Sayisi"])
            else:
                st.info("Haftalık veri henüz işlenmedi.")

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("#### 😊 Duygu Dağılımı")
            if "Duygu" in df.columns:
                sentiment_counts = df["Duygu"].value_counts()
                st.bar_chart(sentiment_counts)
        with col_right:
            st.markdown("#### ⭐ Odak Trendi")
            if "Odak_Puani" in df.columns:
                focus_trend = df[["Tarih", "Odak_Puani"]].sort_values("Tarih")
                st.line_chart(focus_trend.set_index("Tarih")["Odak_Puani"])

        st.markdown("---")
        with st.expander("📋 Tüm Oturum Verilerini Gör"):
            display_df = df.copy()
            display_df["Tarih"] = display_df["Tarih"].dt.strftime("%Y-%m-%d %H:%M")
            st.dataframe(display_df, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Verimlilik Raporu")
        col_pdf1, col_pdf2 = st.columns([2, 1])

        with col_pdf1:
            st.write("Çalışma verilerini Excel ile uyumlu CSV formatında indirebilirsin.")
        with col_pdf2:
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Raporu İndir (Excel)",
                data=csv,
                file_name=f"BeeFocus_Veri_{st.session_state.username}.csv",
                mime="text/csv",
                use_container_width=True,
            )