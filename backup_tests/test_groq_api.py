"""
Test script to verify Groq API connectivity using the key from .env file
"""

import os
from dotenv import load_dotenv
from groq import Groq

def test_groq_api():
    # Load environment variables
    load_dotenv()
    
    # Get the API key
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ ERROR: No API key found in .env file")
        return False
        
    # Mask the key for logging
    masked_key = f"{api_key[:5]}...{api_key[-5:]}"
    print(f"🔑 Found API key in .env file: {masked_key}")
    print(f"📏 API key length: {len(api_key)} characters")
    
    # Initialize Groq client
    client = Groq(api_key=api_key)
    
    try:
        # Simple test query
        print("🔄 Testing API connectivity...")
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test message to verify API connectivity."}
            ],
            temperature=1,
            max_tokens=100
        )
        
        # Get the response
        response = completion.choices[0].message.content
        print(f"✅ API test successful! Received response:")
        print(f"🤖 {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ API test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Groq API Connectivity Test")
    print("=" * 50)
    
    success = test_groq_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TEST PASSED: Groq API connection is working correctly")
    else:
        print("❌ TEST FAILED: Could not connect to Groq API")
    print("=" * 50)
