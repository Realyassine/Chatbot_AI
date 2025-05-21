import requests
import json
import os
import sys
import time

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
BASE_URL = "http://localhost:8001"

def test_backend_connection():
    print_section("Testing Backend Connection")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        
        if response.status_code == 200:
            print_success(f"Backend server is running at {BASE_URL}")
            return True
        else:
            print_error(f"Backend server responded with status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to backend server at {BASE_URL}")
        print_info("Make sure the backend server is running with 'python app.py'")
        return False

def test_auth():
    print_section("Testing Authentication")
    
    # Test registration
    reg_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "password123"
    }
    
    # Also test with known testuser
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    
    print_info(f"Trying to register new user: {reg_data['username']}")
    
    try:
        reg_response = requests.post(f"{BASE_URL}/register", json=reg_data)
        if reg_response.status_code == 201:
            print_success(f"Registration successful for {reg_data['username']}")
            login_data = {
                "username": reg_data["username"],
                "password": reg_data["password"]
            }
        elif reg_response.status_code == 400 and "already registered" in reg_response.text:
            print_warning(f"User already exists, continuing with login")
        else:
            print_error(f"Registration failed: {reg_response.text}")
    except Exception as e:
        print_error(f"Registration request error: {str(e)}")
    
    # Test login
    print_info(f"Attempting to login as: {login_data['username']}")
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/token",
            data=login_data
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data["access_token"]
            print_success(f"Login successful for {login_data['username']}")
            print_info(f"Token: {token[:10]}...{token[-10:]}")
            return token
        else:
            print_error(f"Login failed with status {login_response.status_code}: {login_response.text}")
            return None
    except Exception as e:
        print_error(f"Login request error: {str(e)}")
        return None

def test_me_endpoint(token):
    print_section("Testing User Profile Endpoint")
    
    if not token:
        print_error("No token available, cannot test user profile.")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print_success(f"Successfully retrieved profile for {user_data['username']}")
            print_info(f"Email: {user_data['email']}")
            return True
        else:
            print_error(f"Failed to retrieve user profile: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error accessing user profile: {str(e)}")
        return False

def test_chat(token):
    print_section("Testing Chat Functionality")
    
    if not token:
        print_error("No token available, cannot test chat.")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test chat
    chat_data = {
        "message": "Hello, can you tell me about yourself?",
        "role": "user"
    }
    
    print_info(f"Sending message: '{chat_data['message']}'")
    
    try:
        chat_response = requests.post(
            f"{BASE_URL}/chat/",
            headers=headers,
            json=chat_data
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print_success("Chat message sent and response received")
            print_info(f"AI Response: {response_data['response'][:100]}...")
            print_info(f"Conversation ID: {response_data['conversation_id']}")
            return response_data['conversation_id']
        else:
            print_error(f"Chat failed with status {chat_response.status_code}: {chat_response.text}")
            return None
    except Exception as e:
        print_error(f"Chat request error: {str(e)}")
        return None

def test_conversations(token, conversation_id=None):
    print_section("Testing Conversation Management")
    
    if not token:
        print_error("No token available, cannot test conversations.")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print_info("Fetching all conversations")
    
    try:
        # Get all conversations
        convs_response = requests.get(
            f"{BASE_URL}/conversations/",
            headers=headers
        )
        
        if convs_response.status_code == 200:
            conversations = convs_response.json()["conversations"]
            print_success(f"Found {len(conversations)} conversations")
            
            if len(conversations) > 0:
                for i, conv in enumerate(conversations):
                    print_info(f"  {i+1}. {conv['title']} (ID: {conv['conversation_id']})")
                
                # If no conversation_id was provided, use the first one from the list
                if not conversation_id and len(conversations) > 0:
                    conversation_id = conversations[0]['conversation_id']
                    print_info(f"Using conversation ID: {conversation_id}")
            else:
                print_warning("No conversations found")
                return True
        else:
            print_error(f"Get conversations failed: {convs_response.status_code} - {convs_response.text}")
            return False
    except Exception as e:
        print_error(f"Get conversations error: {str(e)}")
        return False
    
    if not conversation_id:
        print_warning("No conversation ID available, cannot test conversation messages.")
        return False
    
    print_info(f"Fetching messages for conversation: {conversation_id}")
    
    try:
        # Get messages for a conversation
        msgs_response = requests.get(
            f"{BASE_URL}/conversations/{conversation_id}/messages",
            headers=headers
        )
        
        if msgs_response.status_code == 200:
            messages = msgs_response.json()["messages"]
            print_success(f"Found {len(messages)} messages in conversation")
            for i, msg in enumerate(messages):
                print_info(f"  {i+1}. [{msg['role']}]: {msg['content'][:50]}...")
            return True
        else:
            print_error(f"Get messages failed: {msgs_response.status_code} - {msgs_response.text}")
            return False
    except Exception as e:
        print_error(f"Get messages error: {str(e)}")
        return False

def test_conversation_title_update(token, conversation_id):
    print_section("Testing Conversation Title Update")
    
    if not token or not conversation_id:
        print_error("Missing token or conversation ID, cannot test title update.")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    new_title = f"Updated Test Conversation {int(time.time())}"
    print_info(f"Updating conversation title to: '{new_title}'")
    
    try:
        response = requests.put(
            f"{BASE_URL}/conversations/{conversation_id}",
            headers=headers,
            json={"title": new_title}
        )
        
        if response.status_code == 200:
            print_success(f"Successfully updated conversation title")
            return True
        else:
            print_error(f"Title update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Title update error: {str(e)}")
        return False

def test_continue_conversation(token, conversation_id):
    print_section("Testing Continue Conversation")
    
    if not token or not conversation_id:
        print_error("Missing token or conversation ID, cannot test continuing conversation.")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    chat_data = {
        "message": "Tell me more about that topic.",
        "role": "user",
        "conversation_id": conversation_id
    }
    
    print_info(f"Sending follow-up message in conversation {conversation_id}")
    
    try:
        chat_response = requests.post(
            f"{BASE_URL}/chat/",
            headers=headers,
            json=chat_data
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print_success("Follow-up message sent successfully")
            print_info(f"AI Response: {response_data['response'][:100]}...")
            return True
        else:
            print_error(f"Follow-up message failed: {chat_response.status_code} - {chat_response.text}")
            return False
    except Exception as e:
        print_error(f"Follow-up message error: {str(e)}")
        return False

def main():
    print_section("CHATBOT AI SYSTEM TEST")
    
    success = test_backend_connection()
    if not success:
        print_error("Backend connection failed, aborting tests.")
        return
    
    token = test_auth()
    if not token:
        print_error("Authentication failed, aborting tests.")
        return
    
    profile_success = test_me_endpoint(token)
    if not profile_success:
        print_warning("User profile test failed, but continuing...")
    
    conversation_id = test_chat(token)
    if not conversation_id:
        print_error("Chat test failed, cannot continue conversation tests.")
    else:
        conversations_success = test_conversations(token, conversation_id)
        if conversations_success:
            title_success = test_conversation_title_update(token, conversation_id)
            continue_success = test_continue_conversation(token, conversation_id)
    
    print_section("TEST SUMMARY")
    print(f"{Colors.BOLD}The backend API tests are complete.{Colors.ENDC}")
    print(f"Please check the results above to ensure all tests passed.")
    print(f"Next steps:")
    print(f"1. Make sure the frontend is running (cd frontend/chatbotUI && npm run dev)")
    print(f"2. Test the complete application manually by logging in through the frontend")
    print("")

if __name__ == "__main__":
    main()
