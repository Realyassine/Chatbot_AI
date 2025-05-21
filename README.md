# Chatbot AI

**Chatbot AI Project** — A conversational AI chatbot using Python FastAPI, React, and the Groq API with SQLite-based conversation storage

## 🧠 Overview

This project is a complete chatbot application with user authentication, conversation management, and AI-powered chat functionality. It leverages modern frontend technologies to provide a fast, intuitive experience with a clean, responsive interface. The application maintains conversation history in a database and supports text-to-speech and speech-to-text features.

## 🚀 Features

### Backend

- **FastAPI Framework**: High-performance Python API framework for efficient request handling.
- **JWT Authentication**: Secure token-based authentication system with password hashing.
- **Database Integration**: MySQL/SQLite storage for user accounts and conversation history.
- **Groq AI Integration**: Connects to the Groq API for advanced LLM responses.
- **API Error Handling**: Comprehensive error handling for reliable operation.

### Frontend

- **React + Vite**: Modern component-based UI with fast hot module replacement.
- **Context API**: State management for authentication and conversations.
- **Tailwind CSS**: Responsive, utility-first styling for clean UI.
- **Toast Notifications**: User-friendly notifications for status updates and errors.
- **Protected Routes**: Route protection based on authentication status.

### Features

- **User Management**: Registration, login, and user profile features.
- **Conversation Management**: Create, list, update and delete conversations.
- **Real-time Chat**: Send messages and receive AI responses.
- **Text-to-Speech**: Convert chatbot responses to audio.
- **Speech-to-Text**: Upload audio or use microphone for voice input.
- **Error Handling**: Graceful error handling throughout the application.

## 🚀 How to Run

### Backend

1. Navigate to the backend directory:

   ```
   cd "c:\Users\Yassine\Desktop\py projects\Chatbot AI\backend"
   ```

2. Activate the Python environment:

   ```
   ..\new-env\Scripts\activate
   ```

3. Start the backend server:

   ```
   uvicorn app:app --reload
   ```

   The backend server will run at `http://localhost:8000`

### Frontend

1. Navigate to the frontend directory:

   ```
   cd "c:\Users\Yassine\Desktop\py projects\Chatbot AI\frontend\chatbotUI"
   ```

2. Start the frontend development server:

   ```
   npm run dev
   ```

   The frontend will run at `http://localhost:5178`

### Login

Use the test user credentials:

- Username: `testuser`
- Password: `testpass`

## ✅ Important Fixes

- **Port Configuration**: The frontend runs on port 5178 not 5173 (this is assigned dynamically by Vite when port 5173 is already in use)
- **Database**: Using SQLite (chatbot.db) instead of MySQL for simplified deployment
- **Test User**: A test user has been created with username `testuser` and password `testpass`
- **Error Handling**: Improved error formatting in ConversationContext to avoid "[object Object]" messages

## 📁 Project Structure

```
Chatbot_AI/
├── backend/
│   ├── .env                          # Environment variables
│   ├── app.py                        # Main FastAPI application
│   ├── auth.py                       # Authentication functions
│   ├── conversation_utils.py         # Conversation management utilities
│   ├── database.py                   # Database connection and models
│   ├── chatbot.db                    # SQLite database (production uses MySQL)
│   └── requirements.txt              # Python dependencies
├── frontend/
│   └── chatbotUI/
│       ├── public/                   # Static files
│       ├── src/
│       │   ├── components/           # React components
│       │   │   ├── ChatInterface.jsx # Main chat UI component
│       │   │   ├── Dashboard.jsx     # Dashboard layout
│       │   │   ├── Login.jsx         # Login/Register form
│       │   │   └── ...               # Other UI components
│       │   ├── contexts/
│       │   │   ├── AuthContext.jsx   # Authentication context
│       │   │   └── ConversationContext.jsx # Chat conversation context
│       │   ├── utils/                # Utility functions
│       │   ├── App.jsx               # Main React component
│       │   └── main.jsx              # Entry point
│       ├── index.html                # HTML template
│       ├── package.json              # Node.js dependencies
│       ├── tailwind.config.js        # Tailwind CSS config
│       └── vite.config.js            # Vite configuration
└── README.md                         # Project documentation
```

## 🛠️ Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm
- API Key: `https://console.groq.com/keys`

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Realyassine/Chatbot_AI.git
   cd Chatbot_AI
   ```

2. **Set up the backend:**

   ```bash
   cd backend
   pip install -r requirements.txt

   # Create a .env file with your API keys
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

3. **Set up the frontend:**

   ```bash
   cd ../frontend/chatbotUI
   npm install
   ```

4. **Run the project:**

   **Backend:**

   ```bash
   # From the backend directory
   uvicorn app:app --reload
   ```

   **Frontend:**

   ```bash
   # From the frontend/chatbotUI directory
   npm run dev
   ```

5. **Open in browser:**

   Navigate to the URL shown in the terminal (typically `http://localhost:5173` or `http://localhost:5174`) to view the application.

6. **Register a new user or use test credentials:**
   - Username: testuser
   - Password: testpass

## 📦 Build for Production

To create an optimized production build:

```bash
cd frontend/chatbotUI
npm run build
```

The build artifacts will be stored in the `dist/` folder, ready to be deployed.

## 🔄 Data Flow

1. User authenticates through the login form
2. Authentication token is stored and used for subsequent API calls
3. User can create or select conversations from the sidebar
4. Messages are sent to the backend, which forwards them to Groq API
5. AI responses are received and displayed in the chat interface
6. Conversations and messages are stored in the database for persistence

## 🔧 Troubleshooting

### Common Issues

1. **Frontend not loading**

   - Verify that you're accessing the correct port as displayed in the terminal (may be 5173, 5174, etc.)
   - Ensure you have sufficient disk space for the Vite dev server to run
   - Check browser console for JavaScript errors

2. **Backend connection issues**

   - Make sure the backend server is running on port 8000
   - Check for CORS issues in the browser console
   - Verify your Groq API key is correctly set in .env

3. **Authentication problems**

   - Clear browser cookies and local storage
   - Check if the token is being properly saved in localStorage
   - Verify the user exists in the database

4. **"[object Object]" error messages**
   - This issue has been fixed by proper error handling
   - If still occurring, check the browser console for details

### Authentication Issues (401 Errors)

If you're experiencing 401 Unauthorized errors:

1. **Check your login**: Make sure you can successfully log in and see the token in localStorage.
2. **CORS settings**: The backend has been configured to accept requests from localhost ports 5173-5178.
3. **Token validity**: Tokens expire after 7 days by default. Try logging out and back in.
4. **Browser cache/cookies**: Try clearing your browser cache and cookies.

### Database Issues

If you're having database connection problems:

1. The app uses SQLite by default, which should work without configuration.
2. For MySQL, make sure your MySQL server is running and check credentials in `.env`.
3. You can run `setup_mysql_db.py` to initialize the MySQL database.

### Groq API Issues

If AI responses aren't working:

1. Check your Groq API key in the backend `.env` file.
2. The app now provides mock responses if your key is invalid or missing.
3. Make sure you have internet connectivity for the API calls.

## 🛠️ Recent Fixes

- **Fixed 401 Unauthorized errors**: Improved CORS configuration and token handling
- **Improved error handling**: Better error messages and graceful failure in API calls
- **Database flexibility**: Added fallback to SQLite when MySQL is unavailable
- **Better Groq API integration**: Mock responses when key is invalid, improved error handling
- **Frontend stability**: Fixed issues with message sending and display
- **Added start script**: A single batch file to start both frontend and backend

## 🔄 Quick Start

For the fastest startup experience, use the included batch file:

```
cd "c:\Users\Yassine\Desktop\py projects\Chatbot AI"
start_all.bat
```

This will start both the frontend and backend servers and open browser windows for each.

## 📋 API Documentation

Once the backend is running, you can access the API documentation at:

- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)
