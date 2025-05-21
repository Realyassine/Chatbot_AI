# Chatbot AI - Final Delivery

This project structure has been cleaned up for the final delivery. All test files and other unnecessary development-related files have been removed or moved to a backup location.

## Project Structure Overview

The project has been streamlined to include only the essential files needed for production:

### Root Directory
- `requirement.txt` - Contains all required Python dependencies
- `start_all.bat` - Main script to start both backend and frontend
- `install_dependencies.bat` - Script to install all required dependencies
- `DELIVERY_README.md` - Documentation for the delivery
- `DELIVERY_VERIFICATION.md` - Verification steps for the delivery
- `GROQ_API_KEY_GUIDE.md` - Guide for setting up the Groq API key

### Backend Directory (./backend)
- `app.py` - The main FastAPI application
- `auth.py` - Authentication functionality
- `conversation_utils.py` - Conversation management utilities
- `database.py` - Database configuration and models
- `check_dependencies.py` - Utility to verify required dependencies
- `setup_db.py` - Database initialization script
- `create_test_user.py` - Script to create a test user
- `.env` - Environment variables (API keys, etc.)

### Frontend Directory (./frontend/chatbotUI)
- React/Vite application for the user interface

## Getting Started

1. Run `install_dependencies.bat` to install all required dependencies
2. Run `start_all.bat` to start both the backend and frontend servers
3. Access the application at http://localhost:5173

## Login Information
- Username: testuser
- Password: password123

## Note
For development and testing purposes, a backup of the test files can be found in the `backup_tests` directory. These files are not needed for the production deployment.
