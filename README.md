# ASK GEETA AI - Geeta University Web Chatbot

A production-ready, button-based interactive chatbot for Geeta University, built with **Python (FastAPI)** and **Vanilla HTML/CSS/JS**.

## 🚀 Features
- **Landbot-like UI**: Smooth, bubble-based interactive interface.
- **Session Memory**: Remembers user name for the session.
- **Data Driven**: Content loaded from JSON files (scraped from official website).
- **Modular Architecture**: Easy to extend flows.
- **No Database**: Uses in-memory session store for simplicity and speed.

## 📂 Project Structure
```
project/
 ├── app/
 │   ├── main.py          # FastAPI Entry Point
 │   ├── router.py        # API Routes
 │   ├── session.py       # Session Management
 │   ├── data_loader.py   # Data Access Layer
 │   ├── flows/           # Chat Logic Modules
 │   │   ├── schools.py
 │   │   ├── courses.py
 │   │   ├── ...
 ├── data/                # JSON Content (Schools, Courses, etc.)
 ├── static/              # Frontend (HTML, CSS, JS)
 ├── requirements.txt
 ├── README.md
```

## 🛠️ Local Setup

1. **Install Python 3.9+**
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Access Chatbot**:
   Open [http://localhost:8000](http://localhost:8000) in your browser.

## 🌐 Deployment Guide (Hostinger / VPS)

### 1. Prepare Environment
- SSH into your Hostinger VPS.
- Install Python and Pip/Virtualenv.
- Clone or upload this project code.

### 2. DigitalOcean App Platform / Railway / Render (Alternative)
- Push code to GitHub.
- Connect repository.
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 3. Production Run (VPS)
Use `gunicorn` with `uvicorn` workers for better performance.
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```
- Set up Nginx as a reverse proxy to port 8000.
- Install SSL via Certbot.

## 🎨 Customization
- **Logo & Favicon**: Place `logo.jpeg` and `favicon.jpeg` in the `static/` directory.
- **Colors**: Edit `static/style.css` variable `--primary-color`.

## 📝 Data Updates
All content is stored in the `data/` folder. To update course info or fees, simply edit the corresponding `.json` file. No code changes required.

---
**Developed for Geeta University**
