@echo off
echo ==================================================
echo 🤖 AI Support Agent - Starting Both Servers
echo ==================================================
echo.

REM Set the GROQ API Key from environment or .env file
if not defined GROQ_API_KEY (
    echo ⚠️  GROQ_API_KEY not set. Please set it in your environment or .env file
) else (
    echo 🔑 GROQ_API_KEY: ✅ Set
)
echo 🌐 Backend: http://127.0.0.1:8000
echo 🌐 Frontend: http://localhost:5173
echo 📖 API Docs: http://127.0.0.1:8000/docs
echo ⏹️  Press Ctrl+C to stop both servers
echo ==================================================
echo.

REM Start backend in new window
start "Backend Server" cmd /k "cd backend && python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Both servers are starting in separate windows...
echo 🌐 Backend: http://127.0.0.1:8000
echo 🌐 Frontend: http://localhost:5173
echo.
pause
