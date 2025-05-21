"""
Test script to verify the chat endpoint is using the Groq API correctly
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_chat_endpoint():
    # Load environment variables
    load_dotenv()
    
    # The API endpoint
    API_URL = "http://localhost:8001"
    
    # Step 1: Authenticate and get token
    print("\nStep 1: Authenticating...")    login_data = {
        "username": "testuser", 
        "password": "testpass"  # This appears to be the default password
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
        
        # Step 2: Create a new conversation
        print("\nStep 2: Creating conversation...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        create_response = requests.post(
            f"{API_URL}/conversations/create",
            headers=headers,
            json={"title": "Groq API Test"}
        )
        
        if create_response.status_code != 200:
            print(f"❌ Create conversation failed: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
            
        conversation_data = create_response.json()
        conversation_id = conversation_data.get("conversation_id")
        
        if not conversation_id:
            print("❌ No conversation_id received")
            return False
            
        print(f"✅ Created conversation with ID: {conversation_id}")
        
        # Step 3: Send a message that should trigger the real Groq API
        print("\nStep 3: Sending chat message...")
        
        chat_response = requests.post(
            f"{API_URL}/chat",
            headers=headers,
            json={
                "conversation_id": conversation_id,
                "role": "user",
                "message": "Can you tell me something that clearly shows you're the real Groq AI and not a mock response? Include the phrase 'This is a real Groq API response' somewhere in your answer."
            }
        )
        
        if chat_response.status_code != 200:
            print(f"❌ Chat request failed: {chat_response.status_code}")
            print(f"Response: {chat_response.text}")
            return False
            
        chat_data = chat_response.json()
        response = chat_data.get("response")
        
        if not response:
            print("❌ No response received")
            return False
            
        print(f"\n--- AI Response ---\n{response}\n-------------------\n")
        
        # Check if this appears to be a mock response or a real one
        mock_indicators = [
            "mock response",
            "no valid Groq API key",
            "API key is not properly configured",
            "This is a mock response",
            "I'm running in mock mode",
            "simulated response"
        ]
        
        is_mock = any(indicator.lower() in response.lower() for indicator in mock_indicators)
        
        if is_mock:
            print("❌ Appears to be a mock response - Groq API key is not being used correctly")
            return False
        else:
            print("✅ Appears to be a real response from the Groq API")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Chat with Groq API")
    print("=" * 50)
    
    result = test_chat_endpoint()
    
    print("\n" + "=" * 50)
    if result:
        print("✅ TEST PASSED: Chat endpoint is using the Groq API correctly")
    else:
        print("❌ TEST FAILED: Chat endpoint is using mock responses")
    print("=" * 50)
