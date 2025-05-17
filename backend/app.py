import os
from typing import List, Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware
# zedt hado for speech-to-speech

from fastapi.responses import StreamingResponse
import io
import gtts 
import speech_recognition as sr
from tempfile import NamedTemporaryFile

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


if not GROQ_API_KEY:
    raise ValueError("API key for Groq is missing. Please set the GROQ_API_KEY in the .env file.")


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = Groq(api_key=GROQ_API_KEY)


class UserInput(BaseModel):
    message: str
    role: str = "user"
    conversation_id: str
    
class Conversation:
    def __init__(self):
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": "You are a useful AI assistant."}
        ]
        self.active: bool = True

conversations: Dict[str, Conversation] = {}




def query_groq_api(conversation: Conversation) -> str:
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversation.messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with Groq API: {str(e)}")


def get_or_create_conversation(conversation_id: str) -> Conversation:
    if conversation_id not in conversations:
        conversations[conversation_id] = Conversation()
    return conversations[conversation_id]




@app.post("/chat/")
async def chat(input: UserInput):
    conversation = get_or_create_conversation(input.conversation_id)

    if not conversation.active:
        raise HTTPException(
            status_code=400, 
            detail="The chat session has ended. Please start a new session."
        )
        
    try:
        # Append the user's message to the conversation
        conversation.messages.append({
            "role": input.role,
            "content": input.message
        })
        
        response = query_groq_api(conversation)
        
        conversation.messages.append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "conversation_id": input.conversation_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#---------------- function for speech-to-speech # --------------------------

@app.post("/synthesize/")
async def synthesize_speech(data: dict):
    """Convert text to speech using Google's TTS service"""
    try:
        text = data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Generate speech using gTTS
        tts = gtts.gTTS(text=text, lang="en", slow=False)
        
        # Save to BytesIO object
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # Return audio file
        return StreamingResponse(fp, media_type="audio/mpeg")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis error: {str(e)}")

@app.post("/transcribe/")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """Convert speech to text using SpeechRecognition"""
    try:
        # Create a temporary file to store the uploaded audio
        with NamedTemporaryFile(delete=True, suffix='.wav') as temp_audio:
            # Write the uploaded file content to the temporary file
            content = await audio_file.read()
            temp_audio.write(content)
            temp_audio.flush()
            
            # Initialize the recognizer
            recognizer = sr.Recognizer()
            
            # Load the audio file
            with sr.AudioFile(temp_audio.name) as source:
                # Record the audio data from the file
                audio_data = recognizer.record(source)
                
                # Use Google's speech recognition to convert speech to text
                text = recognizer.recognize_google(audio_data)
                
                return {"text": text}
    
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Speech could not be understood")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Could not request results from Google Speech Recognition service: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition error: {str(e)}")

@app.get("/listen-mic/")
async def listen_microphone():
    """Listen to the microphone and convert speech to text"""
    try:
        recognizer = sr.Recognizer()
        
        # Use the default microphone as the audio source
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            print("Listening to microphone...")
            
            # Listen for the first phrase and extract it into audio data
            audio_data = recognizer.listen(source)
            print("Processing speech...")
            
            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio_data)
            return {"text": text}
    
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Speech could not be understood")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Could not request results from Google Speech Recognition service: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition error: {str(e)}")