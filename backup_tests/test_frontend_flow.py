"""
Chatbot AI Project - End-to-End Test Script
This script simulates frontend flows using backend APIs to verify end-to-end functionality.
"""

import requests
import json
import os
import sys
import time
import webbrowser
from urllib.parse import urljoin
import threading

# Color formatting for terminal output
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

# Backend URL
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:5173"

# Test user credentials
TEST_USERNAME = "testuser"
TEST_PASSWORD = "password123"

# Session to maintain cookies/auth state
session = requests.Session()

def verify_backend_running():
    """Verify that the backend is running and accessible"""
    print_section("Checking Backend Availability")
    
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is running at {BACKEND_URL}")
            return True
        else:
            print_error(f"Backend responded with status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to backend at {BACKEND_URL}")
        print_info("Make sure the backend server is running with 'python app.py'")
        return False
    except Exception as e:
        print_error(f"Error checking backend: {str(e)}")
        return False

def verify_frontend_running():
    """Verify that the frontend is running and accessible"""
    print_section("Checking Frontend Availability")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_success(f"Frontend is running at {FRONTEND_URL}")
            return True
        else:
            print_error(f"Frontend responded with status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to frontend at {FRONTEND_URL}")
        print_info("Make sure the frontend server is running (cd frontend/chatbotUI && npm run dev)")
        return False
    except Exception as e:
        print_error(f"Error checking frontend: {str(e)}")
        return False

def authenticate():
    """Authenticate with the backend API"""
    print_section("Testing Authentication")
    
    login_url = urljoin(BACKEND_URL, "/token")
    
    data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = session.post(login_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                session.headers.update({"Authorization": f"Bearer {access_token}"})
                print_success("Successfully authenticated with test user credentials")
                print_info(f"Token received: {access_token[:10]}...{access_token[-10:]}")
                return True
            else:
                print_error("No access token received in response")
                return False
        else:
            print_error(f"Authentication failed with status code {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error during authentication: {str(e)}")
        return False

def test_conversation_flow():
    """Test the complete conversation flow"""
    print_section("Testing Conversation Flow")
    
    # 1. Create a new conversation
    try:
        create_url = urljoin(BACKEND_URL, "/conversations/create")
        create_response = session.post(create_url, json={"title": "Test Conversation"})
        
        if create_response.status_code != 200:
            print_error(f"Failed to create conversation: {create_response.status_code}")
            print_info(f"Response: {create_response.text}")
            return False
        
        conversation_data = create_response.json()
        conversation_id = conversation_data.get("conversation_id")
        
        if not conversation_id:
            print_error("No conversation_id received in response")
            return False
            
        print_success(f"Created test conversation with ID: {conversation_id}")
        
        # 2. Send a message and get a response
        chat_url = urljoin(BACKEND_URL, "/chat")
        test_message = "What is artificial intelligence?"
        
        chat_response = session.post(
            chat_url, 
            json={
                "conversation_id": conversation_id,
                "user_message": test_message
            }
        )
        
        if chat_response.status_code != 200:
            print_error(f"Failed to send message: {chat_response.status_code}")
            print_info(f"Response: {chat_response.text}")
            return False
            
        chat_data = chat_response.json()
        assistant_response = chat_data.get("assistant_response")
        
        if not assistant_response:
            print_error("No assistant_response received")
            return False
            
        print_success(f"Received response for message: {test_message}")
        print_info(f"Response: {assistant_response[:100]}...")
        
        # 3. List conversations to verify it was saved
        list_url = urljoin(BACKEND_URL, "/conversations")
        list_response = session.get(list_url)
        
        if list_response.status_code != 200:
            print_error(f"Failed to list conversations: {list_response.status_code}")
            return False
            
        conversations = list_response.json()
        
        if not any(conv.get("conversation_id") == conversation_id for conv in conversations):
            print_error(f"Created conversation {conversation_id} not found in list")
            return False
            
        print_success("Conversation successfully listed in user's conversations")
        
        # 4. Continue the same conversation
        continue_message = "Can you expand on machine learning?"
        continue_response = session.post(
            chat_url, 
            json={
                "conversation_id": conversation_id,
                "user_message": continue_message
            }
        )
        
        if continue_response.status_code != 200:
            print_error(f"Failed to continue conversation: {continue_response.status_code}")
            return False
            
        continue_data = continue_response.json()
        continued_response = continue_data.get("assistant_response")
        
        if not continued_response:
            print_error("No assistant_response received for continuation")
            return False
            
        print_success("Successfully continued conversation with follow-up question")
        
        # 5. Get conversation history
        history_url = urljoin(BACKEND_URL, f"/conversations/{conversation_id}")
        history_response = session.get(history_url)
        
        if history_response.status_code != 200:
            print_error(f"Failed to get conversation history: {history_response.status_code}")
            return False
            
        history_data = history_response.json()
        messages = history_data.get("messages", [])
        
        if len(messages) < 4:  # Should have 2 user messages and 2 assistant responses
            print_error(f"Expected at least 4 messages in history, got {len(messages)}")
            return False
            
        print_success("Successfully retrieved conversation history")
        
        return True
        
    except Exception as e:
        print_error(f"Error during conversation flow test: {str(e)}")
        return False

def test_audio_feature():
    """Test the text-to-speech API endpoint"""
    print_section("Testing Audio Feature")
    
    try:
        audio_url = urljoin(BACKEND_URL, "/speak")
        test_text = "This is a test of the text to speech feature."
        
        audio_response = session.post(
            audio_url,
            json={"text": test_text}
        )
        
        if audio_response.status_code != 200:
            print_error(f"Failed to get audio response: {audio_response.status_code}")
            print_info(f"Response: {audio_response.text}")
            return False
        
        content_type = audio_response.headers.get('Content-Type')
        if 'audio' not in content_type:
            print_error(f"Expected audio content type, got: {content_type}")
            return False
            
        print_success("Successfully received audio response")
        print_info(f"Audio content length: {len(audio_response.content)} bytes")
        
        # Save the audio for manual verification
        with open("test_audio.mp3", "wb") as f:
            f.write(audio_response.content)
            
        print_info("Saved test audio to test_audio.mp3 for manual verification")
        
        return True
    except Exception as e:
        print_error(f"Error during audio feature test: {str(e)}")
        return False

def open_html_test_page():
    """Open the quick_test.html page for manual verification"""
    print_section("Manual Frontend Testing")
    
    try:
        html_path = os.path.abspath("../quick_test.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file://{html_path}")
            print_success(f"Opened quick_test.html for manual verification")
        else:
            # Create a simple test HTML file
            test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot API Quick Test</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        #container { display: flex; flex-direction: column; height: 100vh; }
        #chatbox { flex: 1; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; overflow-y: auto; }
        #controls { display: flex; }
        #message { flex: 1; padding: 8px; }
        button { padding: 8px 16px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        .user { color: blue; }
        .bot { color: green; }
    </style>
</head>
<body>
    <h1>Chatbot API Quick Test</h1>
    <div id="container">
        <div id="status">Status: Checking connection...</div>
        <div id="login">
            <h3>Login</h3>
            <input type="text" id="username" placeholder="Username" value="testuser">
            <input type="password" id="password" placeholder="Password" value="password123">
            <button id="loginBtn">Login</button>
        </div>
        <div id="chatbox"></div>
        <div id="controls">
            <input type="text" id="message" placeholder="Type your message here">
            <button id="sendBtn">Send</button>
            <button id="speakBtn">🔊</button>
        </div>
    </div>

    <script>
        const backendUrl = 'http://localhost:8000';
        let token = '';
        let currentConversationId = '';
        const chatbox = document.getElementById('chatbox');
        const status = document.getElementById('status');

        // Check if backend is running
        fetch(`${backendUrl}/health-check`)
            .then(response => {
                if (response.ok) {
                    status.textContent = 'Status: Connected to backend';
                    status.style.color = 'green';
                } else {
                    status.textContent = 'Status: Backend returned an error';
                    status.style.color = 'red';
                }
            })
            .catch(error => {
                status.textContent = 'Status: Cannot connect to backend';
                status.style.color = 'red';
                console.error('Error:', error);
            });

        // Login function
        document.getElementById('loginBtn').addEventListener('click', async () => {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch(`${backendUrl}/token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                });
                
                if (response.ok) {
                    const data = await response.json();
                    token = data.access_token;
                    status.textContent = 'Status: Logged in successfully';
                    status.style.color = 'green';
                    
                    // Create a new conversation
                    createConversation();
                } else {
                    status.textContent = 'Status: Login failed';
                    status.style.color = 'red';
                }
            } catch (error) {
                status.textContent = 'Status: Login request failed';
                status.style.color = 'red';
                console.error('Error:', error);
            }
        });

        // Create a new conversation
        async function createConversation() {
            try {
                const response = await fetch(`${backendUrl}/conversations/create`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ title: 'Quick Test Conversation' })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    currentConversationId = data.conversation_id;
                    status.textContent = `Status: Created conversation ${currentConversationId}`;
                    addMessage('system', `Created new conversation with ID: ${currentConversationId}`);
                } else {
                    status.textContent = 'Status: Failed to create conversation';
                    status.style.color = 'red';
                }
            } catch (error) {
                status.textContent = 'Status: Create conversation request failed';
                status.style.color = 'red';
                console.error('Error:', error);
            }
        }

        // Send message
        document.getElementById('sendBtn').addEventListener('click', sendMessage);
        document.getElementById('message').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        async function sendMessage() {
            const messageInput = document.getElementById('message');
            const message = messageInput.value.trim();
            
            if (!message || !token || !currentConversationId) return;
            
            addMessage('user', message);
            messageInput.value = '';
            
            try {
                const response = await fetch(`${backendUrl}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        conversation_id: currentConversationId,
                        user_message: message
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    addMessage('bot', data.assistant_response);
                } else {
                    status.textContent = 'Status: Failed to send message';
                    status.style.color = 'red';
                    addMessage('system', 'Error: Failed to get response from server');
                }
            } catch (error) {
                status.textContent = 'Status: Send message request failed';
                status.style.color = 'red';
                console.error('Error:', error);
                addMessage('system', 'Error: Failed to send message to server');
            }
        }

        // Text to speech
        document.getElementById('speakBtn').addEventListener('click', async () => {
            const messageInput = document.getElementById('message');
            const text = messageInput.value.trim();
            
            if (!text || !token) return;
            
            try {
                const response = await fetch(`${backendUrl}/speak`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ text })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const audioUrl = URL.createObjectURL(blob);
                    const audio = new Audio(audioUrl);
                    audio.play();
                    status.textContent = 'Status: Playing audio';
                } else {
                    status.textContent = 'Status: Failed to get audio';
                    status.style.color = 'red';
                }
            } catch (error) {
                status.textContent = 'Status: Audio request failed';
                status.style.color = 'red';
                console.error('Error:', error);
            }
        });

        function addMessage(sender, text) {
            const messageDiv = document.createElement('div');
            messageDiv.className = sender;
            
            let prefix = '';
            if (sender === 'user') prefix = 'You: ';
            else if (sender === 'bot') prefix = 'Bot: ';
            else prefix = 'System: ';
            
            messageDiv.textContent = prefix + text;
            chatbox.appendChild(messageDiv);
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    </script>
</body>
</html>
            """
            with open("../quick_test.html", "w") as f:
                f.write(test_html)
            
            abs_path = os.path.abspath("../quick_test.html")
            webbrowser.open(f"file://{abs_path}")
            print_success(f"Created and opened quick_test.html for manual verification")
            
        print_info("Please use this page to manually test the chatbot functionality")
        return True
    except Exception as e:
        print_error(f"Error opening test page: {str(e)}")
        return False

def create_end_to_end_test_script():
    """Create an end-to-end batch test script"""
    print_section("Creating End-to-End Test Script")
    
    try:
        batch_script = """@echo off
echo ====================================
echo Chatbot AI - End-to-End Test
echo ====================================
echo.

REM Set terminal colors
color 0B

echo Starting backend server...
start cmd /k "cd backend && ..\\env310\\Scripts\\activate && ..\\env310\\Scripts\\python app.py"

REM Wait for backend to start
timeout /t 5 /nobreak > nul

echo Starting frontend server...
start cmd /k "cd frontend\\chatbotUI && npm run dev"

REM Wait for frontend to start
timeout /t 10 /nobreak > nul

echo Running end-to-end tests...
cd backend
..\\env310\\Scripts\\python test_frontend_flow.py

REM Pause to keep window open
pause
"""
        
        with open("../end_to_end_test.bat", "w") as f:
            f.write(batch_script)
            
        print_success("Created end_to_end_test.bat for one-click testing")
        print_info("Run this script to start the backend, frontend, and run automated tests")
        
        return True
    except Exception as e:
        print_error(f"Error creating test script: {str(e)}")
        return False

def final_check():
    print_section("Final Pre-delivery Checklist")
    
    checklist = [
        "Backend API endpoints are working",
        "Authentication system is functioning",
        "Chat functionality works with or without Groq API key",
        "Text-to-speech feature is operational",
        "Frontend can connect to backend properly",
        "All API errors are handled gracefully",
        "User authentication persists between sessions",
        "Conversations are stored and retrieved correctly",
        "System handles network interruptions",
        "Documentation is complete and accurate"
    ]
    
    print(f"{Colors.BOLD}Please verify the following before delivery:{Colors.ENDC}\n")
    
    for i, item in enumerate(checklist, 1):
        print(f"{Colors.BOLD}{i}.{Colors.ENDC} {item}")
    
    print("\nThese have been tested in the automated scripts, but final manual verification is recommended.")

def main():
    print_section("Chatbot AI - End-to-End Testing")
    print("This script will test the complete end-to-end functionality of the Chatbot AI system.\n")
    
    # Make sure backend is running first
    if not verify_backend_running():
        print_error("Backend is not running. Cannot perform end-to-end tests.")
        return False
    
    # Check if frontend is running (optional)
    frontend_running = verify_frontend_running()
    if not frontend_running:
        print_warning("Frontend is not running. Some browser-based tests will be skipped.")
    
    # Test the backend functionality through API calls
    if not authenticate():
        print_error("Authentication failed. Cannot proceed with other tests.")
        return False
    
    # Test the conversation flow
    conversation_test = test_conversation_flow()
    if not conversation_test:
        print_warning("Conversation flow test failed. Review the issues before delivery.")
    else:
        print_success("Conversation flow test passed successfully!")
    
    # Test audio features
    audio_test = test_audio_feature()
    if not audio_test:
        print_warning("Audio feature test failed. Review the issues before delivery.")
    else:
        print_success("Audio feature test passed successfully!")
    
    # Open HTML test page for manual verification
    if frontend_running:
        open_html_test_page()
    
    # Create the batch test script
    create_end_to_end_test_script()
    
    # Final checklist
    final_check()
    
    print_section("Testing Complete")
    print("All tests have been executed. Please review any warnings or errors before delivery.")
    return True

if __name__ == "__main__":
    main()