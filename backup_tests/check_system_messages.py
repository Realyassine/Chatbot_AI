"""
Simple script to check the current system message
"""
import requests
import sqlite3

def check_system_messages():
    print("\n=== Checking System Messages in Database ===\n")
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('chatbot.db')
        cursor = conn.cursor()
        
        # Query system messages
        cursor.execute("SELECT id, content FROM messages WHERE role = 'system' LIMIT 5")
        system_messages = cursor.fetchall()
        
        if system_messages:
            print(f"Found {len(system_messages)} system messages:")
            for msg_id, content in system_messages:
                print(f"ID {msg_id}: {content}")
                
            # Check if any still have the old message
            old_message_count = 0
            for _, content in system_messages:
                if "You are a useful AI assistant" in content:
                    old_message_count += 1
            
            if old_message_count > 0:
                print(f"\n⚠️ {old_message_count} system messages still have the old text")
            else:
                print("\n✅ No old system messages found")
        else:
            print("No system messages found in database")
            
        conn.close()
    except Exception as e:
        print(f"Database error: {str(e)}")

    print("\n=== Checking API Response ===\n")
    try:
        # Test the API with authentication
        API_URL = "http://localhost:8001"
        
        # First authenticate
        login_data = {
            "username": "testuser",
            "password": "testpass"
        }
        login_response = requests.post(f"{API_URL}/token", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Authentication failed: {login_response.status_code}")
            return
            
        token = login_response.json().get("access_token")
        if not token:
            print("❌ No access token received")
            return
            
        print("✅ Authentication successful")
        
        # Create a new conversation
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        chat_data = {
            "message": "What system instructions do you follow?",
            "role": "user"
        }
        
        chat_response = requests.post(
            f"{API_URL}/chat/",
            headers=headers,
            json=chat_data
        )
        
        if chat_response.status_code != 200:
            print(f"❌ Chat request failed: {chat_response.status_code}")
            return
        
        chat_result = chat_response.json()
        ai_response = chat_result.get("response", "")
        conversation_id = chat_result.get("conversation_id", "")
        
        print("\n=== AI Response ===")
        print(ai_response[:300] + "..." if len(ai_response) > 300 else ai_response)
        print("===================\n")
        
        # Check the conversation messages
        messages_response = requests.get(
            f"{API_URL}/conversations/{conversation_id}/messages",
            headers=headers
        )
        
        if messages_response.status_code != 200:
            print(f"❌ Could not get conversation messages: {messages_response.status_code}")
            return
            
        messages_data = messages_response.json()
        messages = messages_data.get("messages", [])
        
        # Find system message
        system_message = None
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content")
                break
                
        if system_message:
            print(f"System message: {system_message}")
            
            if "You are a useful AI assistant" in system_message:
                print("❌ Old system message is still being used")
            elif "You are an intelligent AI chatbot" in system_message:
                print("✅ New system message is being used")
            else:
                print("❓ Unknown system message")
        else:
            print("❌ No system message found in conversation")
        
    except Exception as e:
        print(f"API test error: {str(e)}")

if __name__ == "__main__":
    check_system_messages()
