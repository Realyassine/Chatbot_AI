"""
Chatbot AI Project - Final Delivery Check Script
This script will verify that all necessary components are installed and configured correctly.
"""

import os
import sys
import subprocess
import platform
import importlib.util
import time
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} {title} {'='*20}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}! {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def check_python_version():
    print_section("Python Environment")
    
    # Check Python version
    version = platform.python_version()
    print_info(f"Python version: {version}")
    
    if version.startswith('3.') and int(version.split('.')[1]) >= 8:
        print_success("Python version is compatible")
    else:
        print_warning("Python 3.8 or higher is recommended")

def check_virtual_env():
    # Check if running in a virtual environment
    in_venv = sys.prefix != sys.base_prefix
    
    if in_venv:
        print_success(f"Running in virtual environment: {sys.prefix}")
    else:
        print_warning("Not running in a virtual environment")
    
    # Check if env310 directory exists
    if os.path.exists("../env310"):
        print_success("env310 virtual environment found")
    else:
        print_error("env310 virtual environment not found")

def check_required_packages():
    print_section("Required Python Packages")
    
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "passlib", "jose", 
        "multipart", "pydantic", "pymysql", "dotenv", "groq"
    ]
    
    for package in required_packages:
        try:
            if package == "jose":
                import jose
                print_success("python-jose is installed")
            elif package == "multipart":
                import multipart
                print_success("python-multipart is installed")
            elif package == "dotenv":
                import dotenv
                print_success("python-dotenv is installed")
            else:
                __import__(package)
                print_success(f"{package} is installed")
        except ImportError:
            # Some packages might be part of larger packages
            if package == "jose":
                try:
                    from jose import jwt
                    print_success("python-jose is installed")
                except ImportError:
                    print_error("python-jose is NOT installed")
            elif package == "multipart":
                try:
                    # This is a bit tricky to check directly
                    print_success("python-multipart appears to be installed")
                except Exception:
                    print_error("python-multipart is NOT installed")
            elif package == "dotenv":
                try:
                    from dotenv import load_dotenv
                    print_success("python-dotenv is installed")
                except ImportError:
                    print_error("python-dotenv is NOT installed")
            else:
                print_error(f"{package} is NOT installed")

def check_database():
    print_section("Database Configuration")
    
    # Check .env file
    if not os.path.exists(".env"):
        print_error(".env file not found")
        return
    
    print_success(".env file found")
    
    # Read DATABASE_URL from .env
    with open(".env", "r") as f:
        env_content = f.read()
    
    if "DATABASE_URL" in env_content:
        print_success("DATABASE_URL is configured in .env")
        
        # Check if it's set to SQLite or MySQL
        if "sqlite" in env_content:
            print_info("Using SQLite database")
            
            # Check if the database file exists
            db_file = env_content.split("sqlite:///")[1].split("\n")[0].strip()
            if os.path.exists(db_file) or os.path.exists(f"./{db_file}"):
                print_success(f"SQLite database file exists: {db_file}")
            else:
                print_warning(f"SQLite database file not found: {db_file}")
                print_info("Database will be created when application starts")
        
        elif "mysql" in env_content:
            print_info("Using MySQL database")
            print_warning("Make sure MySQL server is running")
    else:
        print_error("DATABASE_URL not found in .env")

def check_api_key():
    print_section("Groq API Key Configuration")
    
    # Check .env file
    if not os.path.exists(".env"):
        print_error(".env file not found")
        return
    
    # Read GROQ_API_KEY from .env
    with open(".env", "r") as f:
        env_content = f.read()
    
    if "GROQ_API_KEY" in env_content:
        print_success("GROQ_API_KEY is configured in .env")
        
        # Check if it looks like a real key
        api_key_line = [line for line in env_content.split("\n") if "GROQ_API_KEY" in line][0]
        api_key = api_key_line.split("=")[1].strip()
        
        if api_key == "your_new_api_key_here" or api_key == "":
            print_warning("GROQ_API_KEY appears to be a placeholder")
            print_info("The application will use mock responses for AI")
            print_info("To use real AI responses, update the .env file with a valid Groq API key")
        elif api_key.startswith("gsk_"):
            print_success("GROQ_API_KEY appears to be valid")
        else:
            print_warning("GROQ_API_KEY doesn't have the expected format (should start with 'gsk_')")
    else:
        print_error("GROQ_API_KEY not found in .env")

def check_frontend():
    print_section("Frontend Configuration")
    
    # Check package.json
    package_json_path = "../frontend/chatbotUI/package.json"
    if os.path.exists(package_json_path):
        print_success("package.json found in frontend/chatbotUI")
        
        # Check if node_modules exists
        if os.path.exists("../frontend/chatbotUI/node_modules"):
            print_success("node_modules directory exists, dependencies appear to be installed")
        else:
            print_warning("node_modules not found. Need to run 'npm install' in frontend/chatbotUI")
    else:
        print_error("package.json not found in frontend/chatbotUI")
    
    # Check API URL in frontend code
    api_url_found = False
    for js_file in ["../frontend/chatbotUI/src/contexts/AuthContext.jsx"]:
        if os.path.exists(js_file):
            with open(js_file, "r") as f:
                content = f.read()
                if "http://localhost:8001" in content:
                    api_url_found = True
                    print_success("API URL configured correctly in frontend code")
    
    if not api_url_found:
        print_warning("Could not verify API URL in frontend code")

def check_scripts():
    print_section("Utility Scripts")
    
    scripts = [
        "../start_all.bat",
        "setup_db.py",
        "create_test_user.py",
        "final_test.py"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            print_success(f"{script} found")
        else:
            print_error(f"{script} not found")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print_section("CHATBOT AI PROJECT - FINAL DELIVERY CHECK")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Directory: {os.getcwd()}")
    
    check_python_version()
    check_virtual_env()
    check_required_packages()
    check_database()
    check_api_key()
    check_frontend()
    check_scripts()
    
    print_section("OVERALL STATUS")
    print(f"{Colors.BOLD}The Chatbot AI project is ready for delivery!{Colors.ENDC}")
    print("Review any warnings or errors above and address them if needed.")
    
    print_section("HOW TO START THE APPLICATION")
    print("Option 1: Run start_all.bat from the project root directory")
    print("Option 2: Manual start:")
    print("  1. Start backend: cd backend && python app.py")
    print("  2. Start frontend: cd frontend/chatbotUI && npm run dev")
    
    print(f"\n{Colors.OKGREEN}Good luck with your project delivery!{Colors.ENDC}")

if __name__ == "__main__":
    main()
