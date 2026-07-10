from fastapi import FastAPI, Form, HTTPException, responses, APIRouter, Depends, Request
from fastapi.responses import FileResponse   #to grab the whole file instead of a json response and send it over
from fastapi.staticfiles import StaticFiles

import os   #py module, to interact with the os directly

from pydantic import BaseModel
from database import init_db, DB_NAME
from security import hash_password
import sqlite3




app = FastAPI()



app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("pages"):
    app.mount("/pages", StaticFiles(directory="pages"), name="pages")


#accessing pages
PAGES_DIR = "pages"


@app.get("/")
def index():
    return FileResponse(os.path.join(PAGES_DIR, "index.html")) #os.path.join to resolve directories

@app.get("/profile")
def get_profile():
    return FileResponse(os.path.join(PAGES_DIR, "profile.html"))

@app.get("/explore")
def get_explore():
    return FileResponse(os.path.join(PAGES_DIR, "explore.html"))

@app.get("/progress")
def get_progress():
    return FileResponse(os.path.join(PAGES_DIR, "progress.html"))

@app.get("/assessments")
def get_assessments():
    return FileResponse(os.path.join(PAGES_DIR, "assessments.html"))

@app.get("/sign-in")
def get_signin():
    return FileResponse(os.path.join(PAGES_DIR, "signin.html"))

@app.get("/sign-up")
def get_signup():
    return FileResponse(os.path.join(PAGES_DIR, "signup.html"))




# user database setup and sign up

init_db()

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

@app.post("/auth/register")
async def register_user(user_data: RegisterRequest):
    # 1. Validation Boundary: Ensure passwords match perfectly
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match!")
        
    # 2. Cryptographic Security: Hash the raw password string using bcrypt
    encrypted_pass = hash_password(user_data.password)
    
    # 3. Database Layer: Insert a new row into your SQLite table
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (name, email, hashed_password) VALUES (?, ?, ?)",
            (user_data.name, user_data.email, encrypted_pass)
        )
        conn.commit()
        conn.close()
        
    except sqlite3.IntegrityError:
        # SQLite throws this automatically if an entry breaks a UNIQUE constraint column
        raise HTTPException(status_code=400, detail="This email is already registered!")
        
    # 4. Transmission Response: Notify your JS frontend that the write succeeded
    return {"status": "success", "message": "Account created successfully!"}



# sign in

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
async def login_user(user_data: LoginRequest):
    # 1. Look up the user by email
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, hashed_password FROM users WHERE email = ?", (user_data.email,))
    user = cursor.fetchone()
    conn.close()

    # 2. Guard Clause: If user doesn't exist, exit immediately
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Email or Password!")

    user_id, name, hashed_password = user

    # 3. Cryptographic Verification
    from security import verify_password
    if not verify_password(user_data.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid Email or Password!")

    return {"status": "success", "message": f"Welcome back, {name}!", "user_id": user_id}




# endpoint to extract username and email for profile
@app.get("/api/user/me")
async def get_profile(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Grab the name and email for the specific user matching the query string parameter
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    name, email = user
    return {"name": name, "email": email}