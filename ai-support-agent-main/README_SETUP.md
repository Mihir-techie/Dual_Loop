# 🤖 AI Support Agent - Setup Guide

## ✅ Current Status
- **Backend**: ✅ Running on http://127.0.0.1:8000
- **Frontend**: ✅ Running on http://localhost:5173
- **GROQ API**: ✅ Configured and working

## 🚀 Quick Start Options

### Option 1: Use the Batch File (Easiest for Windows)
```bash
# Double-click this file or run in terminal
start_all.bat
```

### Option 2: Use Python Script
```bash
python start_all.py
```

### Option 3: Manual Start (VS Code Terminal)

#### Backend (Terminal 1):
```bash
cd backend
# Set environment variable first
$env:GROQ_API_KEY="your_groq_api_key_here"
# Start server
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend (Terminal 2):
```bash
cd frontend
npm run dev
```

## 🔧 VS Code Terminal Issues Fixed

### Problem: Backend not starting in VS Code terminal
**Solution**: The GROQ_API_KEY environment variable needs to be set before starting the server.

### Fixed Solutions:
1. **Batch files** that automatically set the environment variable
2. **Python scripts** that handle environment setup
3. **Manual commands** with proper environment variable setting

## 📁 Project Structure
```
ai-support-agent-main/
├── backend/
│   ├── start_backend.bat     # Windows batch file for backend
│   ├── start_backend.py      # Python script for backend
│   ├── requirements.txt      # Python dependencies
│   └── app.py               # FastAPI application
├── frontend/
│   ├── start_frontend.py     # Python script for frontend
│   └── package.json         # Node.js dependencies
├── start_all.bat            # Start both servers (Windows)
├── start_all.py             # Start both servers (Python)
└── README_SETUP.md          # This file
```

## 🌐 Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Chat Endpoint**: `POST /conversations/{id}/chat` (JWT required — see `/docs`)

## 🔑 API Configuration
The GROQ API key is automatically configured in:
- `start_all.bat`
- `start_all.py`
- `start_backend.bat`
- `start_backend.py`

## 📦 Dependencies

### Backend:
```bash
pip install -r backend/requirements.txt
```

### Frontend:
```bash
cd frontend
npm install
```

## 🧪 Testing the API
```bash
# Health
curl http://127.0.0.1:8000/

# Signup → copy access_token from JSON
curl -X POST "http://127.0.0.1:8000/auth/signup" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"demo@example.com\",\"password\":\"password123\",\"display_name\":\"Demo User\",\"memory_consent\":true}"

# Create a conversation (replace TOKEN)
curl -X POST "http://127.0.0.1:8000/conversations" ^
  -H "Authorization: Bearer TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"New chat\",\"channel\":\"chat\"}"

# Chat (replace TOKEN and CONV_ID)
curl -X POST "http://127.0.0.1:8000/conversations/CONV_ID/chat" ^
  -H "Authorization: Bearer TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"My webhook returns 429 — what should I check?\",\"channel\":\"chat\",\"compare_without_memory\":false}"
```

## 🛠️ Troubleshooting

### Backend Issues:
1. **Port 8000 in use**: Change port in startup scripts
2. **Environment variable not set**: Use the provided batch files
3. **Dependencies missing**: Run `pip install -r backend/requirements.txt`

### Frontend Issues:
1. **Port 5173 in use**: Frontend will automatically use next available port
2. **Dependencies missing**: Run `npm install` in frontend directory

### VS Code Terminal Issues:
1. **Use the provided batch files** - they handle environment setup automatically
2. **Set environment variable manually** before starting servers
3. **Use separate terminals** for backend and frontend

## 🎯 Features
- ✅ GROQ API integration with Llama-3.1-8b-instant model
- ✅ Memory functionality for conversation history
- ✅ Sentiment analysis
- ✅ FastAPI backend with auto-reload
- ✅ React frontend with Vite
- ✅ CORS enabled for cross-origin requests
