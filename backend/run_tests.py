#!/usr/bin/env python3
"""
Test runner script for the Insightful API backend
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True

def main():
    """Main test runner"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 Starting Insightful API Backend Test Suite")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Run linting (if available)
    print("\n📋 Running code quality checks...")
    run_command("python -m flake8 app --max-line-length=100 --ignore=E203,W503", "Code linting")
    
    # Run tests
    if not run_command("python -m pytest app/tests/ -v", "Running tests"):
        sys.exit(1)
    
    # Generate coverage report
    run_command("python -m pytest app/tests/ --cov=app --cov-report=html", "Generating coverage report")
    
    print("\n🎉 All tests completed successfully!")
    print("📊 Coverage report generated in htmlcov/index.html")

if __name__ == "__main__":
    main()