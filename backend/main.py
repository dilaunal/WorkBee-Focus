from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="WorkBee Pomodoro API")

# --- VERİTABANI BAĞLANTISI ---
# Eğer bilgisayarında MongoDB kuruluysa direkt çalışır.
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.workbee_db

# --- MODELLER (Veri Yapıları) ---
class Task(BaseModel):
    id: str = None
    title: str
    completed: bool = False

class CoachRequest(BaseModel):
    note: str

# --- ENDPOINTS (API Kapıları) ---

@app.get("/")
async def root():
    return {"status": "WorkBee Backend is Online!"}

# 1. Görevleri Getir
@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    tasks = await db.tasks.find().to_list(100)
    return tasks

# 2. Yeni Görev Ekle
@app.post("/tasks")
async def add_task(task: Task):
    task.id = str(uuid.uuid4())
    await db.tasks.insert_one(task.dict())
    return {"message": "Görev eklendi", "id": task.id}

# 3. AI ODAKLANMA KOÇU (Mantık Katmanı)
@app.post("/ai/coach")
async def get_coach_advice(req: CoachRequest):
    # Burada normalde Gemini veya OpenAI API'si çağrılır.
    # Okul projesi için mantıksal bir simülasyon yapıyoruz:
    note = req.note.lower()
    
    if "yorgun" in note or "uykum" in note:
        advice = "Koç: Beynin yorulmuş görünüyor. 15 dakikalık bir 'Power Nap' (şekerleme) yapmanı öneririm."
    elif "odak" in note or "zor" in note:
        advice = "Koç: Odaklanmakta zorlanıyorsan çalışma alanındaki telefonu başka odaya bırakmayı dene."
    else:
        advice = "Koç: Harika gidiyorsun! Ritmini bozma ve bir sonraki pomodoro için derin bir nefes al."
        
    return {"advice": advice}