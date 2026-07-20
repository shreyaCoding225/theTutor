from fastapi import FastAPI, Form, HTTPException, responses, APIRouter, Depends, Request
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse  #to grab the whole file instead of a json response and send it over
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




# curriculum and contents
CURRICULUM_DB = "curriculum.db"

# for loading explore page
def query_curriculum(query: str, params: tuple = ()):
    import sqlite3
    conn = sqlite3.connect(CURRICULUM_DB)
    conn.row_factory = sqlite3.Row  # Access columns by string key names
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

# 1. Fetch all standalone individual courses for the Explore grid layout
@app.get("/api/courses")
async def get_all_courses():
    return query_curriculum("SELECT * FROM courses")

# 2. Search bar helper route: Get courses mapped to a role name text pattern
@app.get("/api/search-role")
async def search_role_courses(role_name: str):
    sql = """
        SELECT c.* FROM courses c
        JOIN role_courses rc ON c.id = rc.course_id
        JOIN roles r ON r.id = rc.role_id
        WHERE r.name LIKE ?
    """
    # Uses SQL wildcard search like %frontend%
    return query_curriculum(sql, (f"%{role_name}%",))




# for loading course pages into template
@app.get("/api/course-details")
async def get_course_details(id: int):
    conn = sqlite3.connect("curriculum.db")
    cursor = conn.cursor()
    
    # 1. Fetch core course info
    cursor.execute("SELECT id, title, description, difficulty FROM courses WHERE id = ?", (id,))
    course_row = cursor.fetchone()
    
    if not course_row:
        conn.close()
        return {"error": "Course not found"}, 404
        
    course_data = {
        "id": course_row[0],
        "title": course_row[1],
        "description": course_row[2],
        "difficulty": course_row[3],
        "skills": []
    }
    
    # 2. Fetch all related skills linked to this course
    cursor.execute("SELECT name, description FROM skills WHERE course_id = ?", (id,))
    skills_rows = cursor.fetchall()
    
    for row in skills_rows:
        course_data["skills"].append({
            "name": row[0],
            "description": row[1]
        })
        
    conn.close()
    return course_data




@app.get("/course")
async def serve_course_page():
    try:
        # 🎯 Updated to point straight to your 'pages' directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "pages", "course.html")
        
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        error_html = f"""
        <div style="padding: 20px; background: #fee2e2; color: #991b1b; border: 1px solid #f87171; font-family: monospace; border-radius: 8px; margin: 20px;">
            <h3>🛠️ FastAPI Template Error Context</h3>
            <p><strong>Message:</strong> {str(e)}</p>
            <p><strong>Attempted Path:</strong> {template_path if 'template_path' in locals() else 'Failed during path parsing'}</p>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=500)
    


# inside course
@app.get("/workspace", response_class=HTMLResponse)
async def serve_workspace_page(course_id: int, module: str):
    # Define the 3 active modules we are supporting right now
    active_modules = [
        "CSS Grid Layouts", 
        "Asynchronous Fetch Processing", 
        "Custom Hooks Pattern"
    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If it's one of our core three modules, serve the real application canvas
    if module in active_modules:
        template_path = os.path.join(base_dir, "pages", "workspace.html")
    else:
        # Otherwise, gracefully send them to our elegant "Coming Soon" placeholder screen
        template_path = os.path.join(base_dir, "pages", "coming-soon.html")
        
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception:
        return HTMLResponse(content="<h2>Workspace template missing.</h2>", status_code=404)
    

# to load the contents to couse workspace
@app.get("/api/module-steps")
async def get_module_steps(module: str):
    conn = sqlite3.connect("curriculum.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT title, instruction, task, initial_code, verify_keyword, show_sandbox 
        FROM modules_content 
        WHERE module_name = ? 
        ORDER BY step_order ASC
    """, (module,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {"error": "Curriculum details data not found"}, 404
        
    steps_payload = []
    for row in rows:
        steps_payload.append({
            "title": row[0],
            "instruction": row[1],
            "task": row[2],
            "initial_code": row[3],
            "verify_keyword": row[4],
            "show_sandbox": bool(row[5]) # Convert SQLite 0/1 to Boolean
        })
        
    return steps_payload



# updation on module completion
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "curriculum.db")

class ProgressPayload(BaseModel):
    user_id: int
    module_id: str
    step_index: int = 0
    status: str = "completed"

@app.post("/api/complete-module")
async def complete_module(data: ProgressPayload):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Ensure table exists with expected schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module_id TEXT NOT NULL,
                step_index INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                UNIQUE(user_id, module_id)
            )
        """)

        # Upsert user progress
        cursor.execute("""
            INSERT INTO user_progress (user_id, module_id, step_index, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, module_id) 
            DO UPDATE SET status = excluded.status, step_index = excluded.step_index
        """, (data.user_id, data.module_id, data.step_index, data.status))

        conn.commit()
        conn.close()

        return {"status": "success", "message": "Progress recorded successfully"}

    except Exception as e:
        print(f"❌ Error in /api/complete-module: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# to read from user_progress

@app.get("/api/user/completed-modules")
async def get_completed_modules(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT module_id FROM user_progress WHERE user_id = ? AND status = 'completed'", 
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return {"completed_modules": [row[0] for row in rows]}

    except Exception as e:
        print(f"Error in /api/user/completed-modules: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")