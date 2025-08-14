#!/opt/homebrew/bin/python3.11
"""
Local development server without Docker
Run PostgreSQL and Redis separately or use cloud services
"""
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required services are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    print(f"✅ Using Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if venv exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        
        # Install requirements
        pip_path = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
        print("📚 Installing requirements...")
        subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    
    return True

def setup_env():
    """Setup environment variables"""
    if not Path(".env").exists():
        print("📝 Creating .env from template...")
        Path(".env").write_text(Path(".env.example").read_text())
        print("⚠️  Edit .env with your credentials!")
        return False
    return True

def run_server():
    """Run the FastAPI server"""
    print("🚀 Starting QanotAI Backend...")
    
    # Activate venv and run server
    if os.name != 'nt':
        activate_cmd = "source venv/bin/activate && "
    else:
        activate_cmd = "venv\\Scripts\\activate && "
    
    cmd = f"{activate_cmd}uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    
    print("\n" + "="*50)
    print("🎉 Server starting at http://localhost:8000")
    print("📚 API Docs at http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    
    if not setup_env():
        print("\n⚠️  Please configure .env before running!")
        sys.exit(1)
    
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")