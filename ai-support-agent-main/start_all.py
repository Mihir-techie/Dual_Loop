#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time

# Load GROQ API key from environment
# Make sure to set GROQ_API_KEY in your environment or create a .env file
if 'GROQ_API_KEY' not in os.environ:
    print('⚠️  Warning: GROQ_API_KEY not set in environment')

def start_backend():
    """Start the backend server"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    print("🚀 Starting Backend Server...")
    print(f"🔑 GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Not set'}")
    
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped gracefully.")

def start_frontend():
    """Start the frontend server"""
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    os.chdir(frontend_dir)
    
    print("🚀 Starting Frontend Server...")
    
    try:
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped gracefully.")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI Support Agent - Starting Both Servers")
    print("=" * 60)
    print("🌐 Backend: http://127.0.0.1:8000")
    print("🌐 Frontend: http://localhost:5173")
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    print("⏹️  Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend in the main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n👋 All servers stopped gracefully.")
