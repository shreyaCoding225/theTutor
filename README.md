# 🎓 theTutor

A secure, responsive full-stack workspace ecosystem designed for student productivity and task organization. **theTutor** features a robust asynchronous backend powered by FastAPI, persistent user session authentication tracking, and a dynamic user interface complete with automatic interface locking for unauthenticated visitors.

---

## 📖 About the Project

**theTutor** was born out of a simple observation: modern digital learning environments are scattered. Students frequently battle context switching—moving between chaotic task lists, lecture schedules, and fragmented study trackers, which breaks focus and adds unnecessary friction to the learning journey. 

This project bridges that gap by engineering a centralized, highly secure productivity workspace. At its core, the project focuses on two foundational pillars: **absolute data isolation** and a **frictionless user experience**. 

Rather than adopting heavy, over-engineered frameworks, the architecture deliberately utilizes a streamlined, performance-first stack:
* **The Performance Engine:** A highly performant FastAPI backend paired with serverless SQLite data streams ensures near-zero latency when processing user information and task updates.
* **The Secure Viewport Guard:** The front-end interaction layers utilize native browser memory pipelines (`localStorage`) coupled with custom CSS glassmorphic overlays. This setup ensures that if a user session expires or a guest attempts to breach the interface, the app immediately intercepts the event at the browser boundary—frosting over the private dashboard area while keeping the main structural layout beautifully intact.

Designed with responsiveness and scalability in mind, **theTutor** serves as a robust baseline for multi-database architectures, built to scale seamlessly from basic profile logging to a fully real-time Kanban task management board.

---

## 🚀 Key Features

* **Asynchronous API Engine:** Built using FastAPI for rapid request handling and optimal backend execution speeds.
* **Persistent Session Bridge:** Leverages browser `localStorage` pipelines to keep users logged in seamlessly across page reboots and browser closures.
* **Responsive Auth Gate:** An overlay architecture that dynamically freezes and frosts over (`backdrop-filter: blur`) the dashboard viewport if an unauthenticated user attempts to view private workspace spaces, while keeping structural header navbars completely active and operational.
* **Relational Data Storage:** Utilizes a localized SQLite database engine for fast, serverless database interactions.

---

## 🛠️ Project Tech Stack

* **Backend:** FastAPI (Python 3.14+)
* **Database:** SQLite3 / SQLAlchemy
* **Frontend:** Semantic HTML5, CSS3 (Flexbox/Grid positioning layouts), Vanilla JavaScript (ES6 Modules)

---

## 🏁 Getting Started Locally

### 1. Clone the repository
```bash
git clone [https://github.com/shreyaCoding225/theTutor.git](https://github.com/shreyaCoding225/theTutor.git)
cd theTutor
```

### 2. Activate the Virtual Environment
```PowerShell
# On Windows PowerShell:
.\fastapi-env\Scripts\Activate.ps1
```

### 3. Spin Up the Development Server
```bash
uvicorn main:app --reload
```

Open your browser and navigate to http://127.0.0.1:8000 to interact with the system live!
