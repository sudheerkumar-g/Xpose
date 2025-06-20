from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import io
import torch
import torchvision.transforms as transforms
import torch.nn as nn
import torchvision.models as models
import sqlite3

# ---------- Initialize FastAPI ----------
app = FastAPI()

# ---------- CORS Setup ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Adjust if frontend URL changes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DB Initialization ----------
def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- Pydantic Models ----------
class User(BaseModel):
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    username: str
    password: str

# ---------- ML Model Setup ----------
model = models.resnet50(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, 3)
state_dict = torch.load("xpose_epoch_8.pth", map_location=torch.device("cpu"))
if not os.path.exists(model_path):
    gdown.download("https://drive.google.com/uc?id=YOUR_FILE_ID", model_path, quiet=False)
model.load_state_dict(state_dict)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

class_names = ['AI-generated', 'Edited', 'Real']

# ---------- API Endpoints ----------

@app.post("/signup")
def signup(user: User):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (user.username,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (user.username, user.email, user.password))
    conn.commit()
    conn.close()
    return {"message": "Signup successful"}

@app.post("/login")
def login(user: LoginUser):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user.username, user.password))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    conn.close()
    return {"message": "Login successful"}

@app.post("/analyze/")
async def analyze_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)
        result = class_names[predicted.item()]

    return {"result": result}

@app.get("/")
def read_root():
    return {"message": "Xpose backend is working!"}
