import io
from gtts import gTTS
import os

def test_tts():
    """Test gtts functionality"""
    try:
        print("Testing gTTS functionality")
        text = "This is a test of the text to speech system"
        
        # Try method 1: Save to file
        print("Method 1: Saving to file...")
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save("test_output.mp3")
        
        if os.path.exists("test_output.mp3"):
            print("✅ File created successfully!")
            file_size = os.path.getsize("test_output.mp3")
            print(f"File size: {file_size} bytes")
        else:
            print("❌ File creation failed")
            
        # Try method 2: Save to BytesIO
        print("\nMethod 2: Using BytesIO...")
        try:
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            bytes_size = len(fp.getvalue())
            print(f"✅ BytesIO successful! Size: {bytes_size} bytes")
        except Exception as e:
            print(f"❌ BytesIO failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    print("Starting TTS test...")
    test_tts()
    print("TTS test complete.")
