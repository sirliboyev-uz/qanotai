#!/usr/bin/env python3
"""Quick start script - minimal dependencies"""
import subprocess
import sys
import os

print("🚀 QanotAI Quick Start")
print("=" * 50)

# Create venv if needed
if not os.path.exists("venv"):
    print("📦 Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])

# Install minimal requirements
print("📚 Installing minimal dependencies...")
pip = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
subprocess.run([pip, "install", "-r", "requirements-minimal.txt"])

# Create .env if needed
if not os.path.exists(".env"):
    print("📝 Creating basic .env...")
    with open(".env", "w") as f:
        f.write("""SECRET_KEY=change-this-to-random-32-character-string
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/qanotai
DEBUG=true
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8100"]
""")

print("\n✅ Setup complete!")
print("\n🎯 To start the server:")
print("   source venv/bin/activate")
print("   uvicorn app.main:app --reload")
print("\n📚 API docs at: http://localhost:8000/docs")