import requests
import json
import sys

# Backend URL
BASE_URL = "http://localhost:8000"

def test_auth():
    print("\n=== Testing Authentication ===")
    
    # Test registration
    reg_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123"
    }
    
    try:
        reg_response = requests.post(f"{BASE_URL}/register", json=reg_data)
        print(f"Registration response status: {reg_response.status_code}")
        if reg_response.status_code == 201:
            print("Registration successful!")
        elif reg_response.status_code == 400:
            print("User already exists, continuing with login")
        else:
            print(f"Registration failed: {reg_response.text}")
    except Exception as e:
        print(f"Registration request error: {str(e)}")
    
    # Test login
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    
    try:
        # OAuth2 login requires form data, not JSON
        login_response = requests.post(
            f"{BASE_URL}/token",
            data=login_data
        )
        
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data["access_token"]
            print("Login successful!")
            print(f"Token: {token[:10]}...{token[-10:]}")
            return token
        else:
            print(f"Login failed: {login_response.text}")
            return None
    except Exception as e:
        print(f"Login request error: {str(e)}")
        return None

def test_user_info(token):
    print("\n=== Testing User Info ===")
    
    if not token:
        print("No token available, cannot test user info.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers=headers
        )
        
        print(f"User info response status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("User info retrieved successfully!")
            print(f"Username: {user_data['username']}")
            print(f"Email: {user_data['email']}")
        else:
            print(f"User info retrieval failed: {response.text}")
    except Exception as e:
        print(f"User info request error: {str(e)}")

def test_chat(token):
    print("\n=== Testing Chat Functionality ===")
    
    if not token:
        print("No token available, cannot test chat.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test chat
    chat_data = {
        "message": "Hello, can you tell me about yourself?",
        "role": "user"
    }
    
    try:
        chat_response = requests.post(
            f"{BASE_URL}/chat/",
            headers=headers,
            json=chat_data
        )
        
        print(f"Chat response status: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print("Chat successful!")
            print(f"AI Response: {response_data['response'][:100]}...")
            print(f"Conversation ID: {response_data['conversation_id']}")
            return response_data['conversation_id']
        else:
            print(f"Chat failed: {chat_response.text}")
            return None
    except Exception as e:
        print(f"Chat request error: {str(e)}")
        return None

def test_conversations(token, conversation_id):
    print("\n=== Testing Conversation Management ===")
    
    if not token:
        print("No token available, cannot test conversations.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get all conversations
        convs_response = requests.get(
            f"{BASE_URL}/conversations/",
            headers=headers
        )
        
        print(f"Get conversations response status: {convs_response.status_code}")
        
        if convs_response.status_code == 200:
            conversations = convs_response.json()["conversations"]
            print(f"Found {len(conversations)} conversations")
            for i, conv in enumerate(conversations):
                print(f"  {i+1}. {conv['title']} (ID: {conv['conversation_id']})")
        else:
            print(f"Get conversations failed: {convs_response.text}")
    except Exception as e:
        print(f"Get conversations error: {str(e)}")
    
    if not conversation_id:
        print("No conversation ID available, skipping conversation messages test.")
        return
    
    try:
        # Get messages for a conversation
        msgs_response = requests.get(
            f"{BASE_URL}/conversations/{conversation_id}/messages",
            headers=headers
        )
        
        print(f"Get messages response status: {msgs_response.status_code}")
        
        if msgs_response.status_code == 200:
            messages = msgs_response.json()["messages"]
            print(f"Found {len(messages)} messages in conversation")
            for i, msg in enumerate(messages):
                print(f"  {i+1}. [{msg['role']}]: {msg['content'][:50]}...")
        else:
            print(f"Get messages failed: {msgs_response.text}")
    except Exception as e:
        print(f"Get messages error: {str(e)}")

def test_error_handling(token):
    print("\n=== Testing Error Handling ===")
    
    if not token:
        print("No token available, cannot test error handling.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test invalid conversation ID
    try:
        response = requests.get(
            f"{BASE_URL}/conversations/invalid_id_123/messages",
            headers=headers
        )
        
        print(f"Invalid conversation ID response status: {response.status_code}")
        print(f"Error message: {response.text}")
    except Exception as e:
        print(f"Request error: {str(e)}")
    
    # Test missing authorization
    try:
        response = requests.get(f"{BASE_URL}/conversations/")
        
        print(f"Missing auth response status: {response.status_code}")
        print(f"Error message: {response.text}")
    except Exception as e:
        print(f"Request error: {str(e)}")

def main():
    print("===== CHATBOT API TEST CLIENT =====")
    
    # Test authentication
    token = test_auth()
    
    if not token:
        print("\nAuthentication failed. Cannot proceed with further tests.")
        sys.exit(1)
    
    # Test user info
    test_user_info(token)
    
    # Test chat
    conversation_id = test_chat(token)
    
    # Test conversations
    test_conversations(token, conversation_id)
    
    # Test error handling
    test_error_handling(token)
    
    print("\n===== TEST COMPLETED =====")
    print("Backend API is functioning correctly!")

if __name__ == "__main__":
    main()