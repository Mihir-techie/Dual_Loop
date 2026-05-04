@echo off
echo 🚀 Starting AI Support Agent Backend...
echo.

REM Set your key here for this session only, or use backend\.env (recommended):
REM set GROQ_API_KEY=your_key_here

if defined GROQ_API_KEY (echo 🔑 GROQ_API_KEY: ✅ Set) else (echo 🔑 GROQ_API_KEY: use backend\.env or: set GROQ_API_KEY=your_key_here)
echo 🌐 Server will be available at: http://127.0.0.1:8000
echo 📖 API Documentation: http://127.0.0.1:8000/docs
echo ⏹️  Press Ctrl+C to stop the server
echo ==================================================

REM Start the FastAPI server
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

pause
