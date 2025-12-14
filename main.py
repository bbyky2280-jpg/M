from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import jwt
from datetime import datetime, timedelta

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "STS99_SECRET_KEY"
ALGORITHM = "HS256"

fake_users = {}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Token invalid or expired")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register-user")
async def register_user(username: str, password: str):
    if username in fake_users:
        return {"status": "error", "msg": "มีผู้ใช้นี้แล้ว"}
    fake_users[username] = {"username": username, "password": password}
    return {"status": "success", "msg": "สมัครสำเร็จ"}

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    username = form.username
    password = form.password

    user = fake_users.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=400, detail="ข้อมูลผิด")

    token = create_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/do-task")
def do_task(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    return {"status": "success", "msg": f"ทำงานแทนผู้ใช้ {user['sub']} สำเร็จ!"}
