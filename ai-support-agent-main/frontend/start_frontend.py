#!/usr/bin/env python3
import os
import sys
import subprocess

print("🚀 Starting AI Support Agent Frontend...")
print("🌐 Frontend will be available at: http://localhost:5173")
print("⏹️  Press Ctrl+C to stop the server")
print("-" * 50)

# Change to frontend directory and start the development server
frontend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(frontend_dir)

try:
    subprocess.run(["npm", "run", "dev"])
except KeyboardInterrupt:
    print("\n👋 Frontend server stopped gracefully.")
