from fastapi import FastAPI, Form, HTTPException, responses, APIRouter, Depends, Request
from fastapi.responses import FileResponse, RedirectResponse  #to grab the whole file instead of a json response and send it over
from fastapi.staticfiles import StaticFiles

import os   #py module, to interact with the os directly

from pydantic import BaseModel
from database import init_db, DB_NAME, verify_or_create_google_user
from security import hash_password
import sqlite3

import httpx
from dotenv import load_dotenv


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





# google sign in btn

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = "http://localhost:8000/auth/callback"

@app.get("/auth/login")
async def login_google():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(url=google_auth_url)


# Callback route where Google routes the user after a successful sign-in
@app.get("/auth/callback")
async def auth_callback(code: str):
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing from Google.")

    # Exchange the temporary code for an access token token loop
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        # Step A: Request the token package
        token_response = await client.post(token_url, data=data)
        token_data = token_response.json()
        
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data.get("error_description"))

        access_token = token_data.get("access_token")

        # Step B: Use token to fetch user profile payload info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = await client.get(user_info_url, headers=headers)
        user_profile = user_response.json()

    #  THIS IS YOUR DATA PACKET:
    # user_profile contains: user_profile['email'], user_profile['name'], user_profile['picture']
    print("Google User Payload details verified successfully:", user_profile)
    
    user_email = user_profile.get("email")
    user_name = user_profile.get("name")
    
    # Run the database verification pipeline check loop
    internal_user_id = verify_or_create_google_user(user_email, user_name)
    
    #  Redirection Bridge: Send them straight to the profile frontend template page.
    # We pass the internal_user_id as a temporary query parameter so the frontend can grab it.
    return RedirectResponse(url=f"http://localhost:8000/profile?auth_session={internal_user_id}")