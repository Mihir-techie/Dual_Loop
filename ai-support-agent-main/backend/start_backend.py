#!/usr/bin/env python3
import os
import sys
import subprocess

# Prefer GROQ_API_KEY from the environment or a backend/.env file (loaded by the app via python-dotenv).
print("🚀 Starting AI Support Agent Backend...")
print(f"🔑 GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Not set (add backend/.env or export GROQ_API_KEY)'}")
print("🌐 Server will be available at: http://127.0.0.1:8000")
print("📖 API Documentation: http://127.0.0.1:8000/docs")
print("⏹️  Press Ctrl+C to stop the server")
print("-" * 50)

# Start the FastAPI server
try:
    subprocess.run([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])
except KeyboardInterrupt:
    print("\n👋 Backend server stopped gracefully.")
