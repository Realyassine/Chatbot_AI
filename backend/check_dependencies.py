"""
Final dependency check for Chatbot AI project.
This script verifies that all required packages are installed.
"""

import importlib.util
import sys
import os

# Define color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Function to check if a package is installed
def check_package(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"{Colors.RED}✗ {package_name} is NOT installed{Colors.ENDC}")
        return False
    else:
        version = get_package_version(package_name)
        print(f"{Colors.GREEN}✓ {package_name} is installed{Colors.ENDC} (version: {version})")
        return True

# Get package version
def get_package_version(package_name):
    try:
        if package_name == "groq":
            import groq
            return groq.__version__
        elif package_name == "fastapi":
            import fastapi
            return fastapi.__version__
        elif package_name == "uvicorn":
            import uvicorn
            return uvicorn.__version__
        elif package_name == "sqlalchemy":
            import sqlalchemy
            return sqlalchemy.__version__
        elif package_name == "pydantic":
            import pydantic
            return pydantic.__version__
        elif package_name == "python-jose":
            import jose
            return jose.__version__
        elif package_name == "passlib":
            import passlib
            return passlib.__version__
        elif package_name == "dotenv":
            import dotenv
            return dotenv.__version__
        elif package_name == "gtts":
            import gtts
            return gtts.__version__
        elif package_name == "speech_recognition":
            import speech_recognition
            return speech_recognition.__version__
        else:
            return "unknown"
    except:
        return "unknown"

def main():
    print(f"\n{Colors.BOLD}Chatbot AI - Dependency Check{Colors.ENDC}")
    print("=" * 50)
    print("Checking required packages...")
    
    # List of required packages
    required_packages = [
        "fastapi", 
        "uvicorn", 
        "sqlalchemy", 
        "pydantic",
        "jose",  # python-jose
        "passlib",
        "dotenv",  # python-dotenv
        "groq",
        "gtts",
        "speech_recognition"
    ]
    
    missing_packages = []
    
    # Check each package
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    print("\n" + "=" * 50)
    
    # Summary
    if missing_packages:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some packages are missing!{Colors.ENDC}")
        print("\nPlease install the missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All required packages are installed!{Colors.ENDC}")
        print("\nYour environment is ready for delivery.")
        return True

if __name__ == "__main__":
    main()
