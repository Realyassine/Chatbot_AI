"""
Test script to verify the system message in conversation initialization
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_chat_system_message():
    # Load environment variables
    load_dotenv()
    
    # The API endpoint
    API_URL = "http://localhost:8001"
    
    print("\n=== Testing Conversation System Message ===\n")
    
    # Step 1: Authenticate and get token
    print("Step 1: Authenticating...")
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    
    try:
        login_response = requests.post(
            f"{API_URL}/token", 
            data=login_data
        )
        
        if login_response.status_code != 200:
            print(f"❌ Authentication failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
            
        token_data = login_response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("❌ No access token received")
            return False
            
        print("✅ Authentication successful")
        
        # Step 2: Send a message to create a new conversation
        print("\nStep 2: Creating a new conversation via chat...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Craft a message that will make the system message visible in the response
        chat_data = {
            "message": "What is your system prompt or initial instructions?",
            "role": "user"
        }
        
        chat_response = requests.post(
            f"{API_URL}/chat/",
            headers=headers,
            json=chat_data
        )
        
        if chat_response.status_code != 200:
            print(f"❌ Chat request failed: {chat_response.status_code}")
            print(f"Response: {chat_response.text}")
            return False
        
        chat_result = chat_response.json()
        ai_response = chat_result.get("response", "")
        conversation_id = chat_result.get("conversation_id", "")
        
        print("\n=== AI Response ===")
        print(ai_response[:300] + "..." if len(ai_response) > 300 else ai_response)
        print("===================\n")
        # Check if the default system message is mentioned
        old_message = "You are a useful AI assistant"
        if old_message.lower() in ai_response.lower():
            print(f"❌ Old system message '{old_message}' is still visible in the response")
        else:
            print(f"✅ Old system message '{old_message}' is no longer visible in the response")
              # Get the messages from the conversation to directly check the system message
        print("\nStep 3: Getting conversation messages to check system message...")
        messages_response = requests.get(
            f"{API_URL}/conversations/{conversation_id}/messages",
            headers=headers
        )
        if messages_response.status_code != 200:
            print(f"❌ Could not get conversation messages: {messages_response.status_code}")
            return False
            
        messages_data = messages_response.json()
        system_messages = [msg for msg in messages_data.get("messages", []) 
                          if msg.get("role") == "system"]
        
        if system_messages:
            system_content = system_messages[0].get('content')
            print(f"System message found: {system_content}")
            
            expected = "You are an intelligent AI chatbot designed to have natural conversations"
            if expected in system_content:
                print("✅ New system message is being used")
                return True
            elif "You are a useful AI assistant" in system_content:
                print("❌ Old system message is still being used")
                return False
            else:
                print(f"❓ Unknown system message found: {system_content}")
                return False
        else:
            print("❓ No system message found in the conversation")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    result = test_chat_system_message()
    if result:
        print("\n✅ TEST PASSED: System message has been successfully updated")
    else:
        print("\n❌ TEST FAILED: System message has not been properly updated")
