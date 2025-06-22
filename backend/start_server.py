#!/usr/bin/env python3
"""
Startup script for the Insightful API backend
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from .env.example...")
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ .env file created. Please update it with your configuration.")
        else:
            print("❌ .env.example file not found. Please create .env manually.")
            return False
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Failed to install dependencies: {result.stderr}")
        return False
    print("✅ Dependencies installed successfully")
    return True

def run_migrations():
    """Run database migrations"""
    print("🗄️  Running database migrations...")
    
    # Initialize Alembic if not already done
    if not Path("alembic/versions").exists():
        print("Initializing Alembic...")
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"])
    
    # Run migrations
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️  Migration warning: {result.stderr}")
        print("This might be expected if database doesn't exist yet.")
    else:
        print("✅ Database migrations completed")
    return True

def start_server(host="0.0.0.0", port=12000):
    """Start the FastAPI server"""
    print("🚀 Starting Insightful API server...")
    print("Server will be available at:")
    print(f"  - Local: http://localhost:{port}")
    print(f"  - External: https://work-1-fjkxjusgmutlbdfd.prod-runtime.all-hands.dev")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", host, 
            "--port", str(port),
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main startup function"""
    print("🏢 Insightful API Backend Startup")
    print("=" * 40)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Start the Insightful API server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=12000, help='Port to bind to')
    args = parser.parse_args()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Run migrations
    run_migrations()
    
    # Start server
    start_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()