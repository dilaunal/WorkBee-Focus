import json
import os
import hashlib
from datetime import datetime

USERS_FILE = "data/users.json"
os.makedirs("data", exist_ok=True)

def load_users():
    """Kullanıcıları yükle"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Kullanıcıları kaydet"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """Basit şifre hashleme (production için daha güvenli yöntem kullanılmalı)"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Yeni kullanıcı kaydet"""
    users = load_users()
    
    if username in users:
        return False, "Bu kullanıcı adı zaten kullanılıyor!"
    
    users[username] = {
        "password_hash": hash_password(password),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_users(users)
    return True, "Kayıt başarılı!"

def login_user(username, password):
    """Kullanıcı girişi"""
    users = load_users()
    
    if username not in users:
        return False, "Kullanıcı adı bulunamadı!"
    
    if users[username]["password_hash"] != hash_password(password):
        return False, "Şifre yanlış!"
    
    return True, "Giriş başarılı!"


