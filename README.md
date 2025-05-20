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

## 🔌 API Endpoints

The backend provides the following endpoints:

### Chat Endpoints

- `POST /chat/`: Send messages to the AI chatbot

### Speech Endpoints

- `POST /synthesize/`: Convert text to speech
- `POST /transcribe/`: Convert uploaded audio to text
- `GET /listen-mic/`: Convert speech from microphone to text

### Authentication Endpoints

- `POST /register`: Create a new user account
- `POST /token`: Login and get access token
- `GET /users/me`: Get current user details

### Conversation Management

- `GET /conversations/`: Get all user conversations
- `GET /conversations/{conversation_id}/messages`: Get messages from a specific conversation
- `PUT /conversations/{conversation_id}`: Update conversation title
- `DELETE /conversations/{conversation_id}`: Delete a conversation

```

```
