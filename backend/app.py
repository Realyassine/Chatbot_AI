import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# zedt hado for speech-to-speech
from fastapi.responses import StreamingResponse
import io

# Import our custom modules
from database import create_tables, get_db
from auth import (
    Token, UserCreate, UserResponse, authenticate_user, create_access_token,
    get_current_active_user, create_user, get_user
)
import conversation_utils as conv_utils
import gtts 
import speech_recognition as sr
from tempfile import NamedTemporaryFile

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


if not GROQ_API_KEY:
    raise ValueError("API key for Groq is missing. Please set the GROQ_API_KEY in the .env file.")


app = FastAPI()

# Initialize database tables
create_tables()

# Define frontend origins - make sure all your frontend URLs are included
frontend_origins = [
    "http://localhost:5173",
    "http://localhost:5174", 
    "http://localhost:5175", 
    "http://localhost:5178",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5178",
]

# Configure CORS middleware with appropriate settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Authorization"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


client = Groq(api_key=GROQ_API_KEY)


class UserInput(BaseModel):
    message: str
    role: str = "user"
    conversation_id: Optional[str] = None

class ConversationList(BaseModel):
    conversations: List[conv_utils.ConversationResponse]
    
    class Config:
        from_attributes = True

class MessageList(BaseModel):
    messages: List[conv_utils.MessageResponse]
    
    class Config:
        from_attributes = True

# For memory cache of active conversations
class Conversation:
    def __init__(self, messages=None):
        # Define our custom system message
        default_system_message = {"role": "system", "content": "You are an intelligent AI chatbot designed to have natural conversations. Respond in a helpful and informative way."}
        
        if messages:
            # Make a copy of messages to avoid modifying the original list
            self.messages = list(messages)
            
            # Check for a system message and update/add as needed
            system_found = False
            for i, msg in enumerate(self.messages):
                if msg.get("role") == "system":
                    # Update existing system message to the desired one
                    self.messages[i] = default_system_message
                    system_found = True
                    break
            
            # If no system message found, add one at the beginning
            if not system_found:
                self.messages.insert(0, default_system_message)
        else:
            # No messages provided, start with our default system message
            self.messages = [default_system_message]
        
        self.active: bool = True

conversations: Dict[str, Conversation] = {}




def query_groq_api(conversation: Conversation) -> str:
    try:
        # Use the global GROQ_API_KEY that was already loaded from .env at startup
        api_key = GROQ_API_KEY
        
        # Check if this is a development environment or invalid API key
        if not api_key or api_key == "your_new_api_key_here":
            print("Using mock response (API key is missing or appears to be a placeholder)")
            
            # Get the latest user message for context
            user_message = "Hello"
            for msg in conversation.messages:
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break
            
            # Generate a deterministic but varied mock response based on the message content
            mock_responses = [
                f"This is a mock response since no valid Groq API key was found. You asked about: '{user_message}'",
                f"I'm running in mock mode without a Groq API key. In response to your query about '{user_message}', I would typically provide a thoughtful answer.",
                f"Hello! The Groq API key appears to be invalid or missing. In a real scenario, I would analyze your message: '{user_message}' and give a detailed response.",
                f"Mock AI Assistant: Your message was '{user_message}'. To get real AI responses, please update the GROQ_API_KEY in the .env file.",
                f"I notice you mentioned '{user_message}'. This is a simulated response since the Groq API key is not properly configured."
            ]
            
            # Select a response based on the hash of the user message to ensure variety
            import hashlib
            message_hash = int(hashlib.md5(user_message.encode()).hexdigest(), 16)
            selected_response = mock_responses[message_hash % len(mock_responses)]
            
            return selected_response
        
        # Try to use the actual Groq API
        try:
            # Mask API key in logs for security
            masked_key = f"{api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}"
            print(f"Calling Groq API with key: {masked_key}")
            print(f"API key length: {len(api_key)} characters")
            
            # Reinitialize the client with the current API key to ensure it's using the latest value
            groq_client = Groq(api_key=api_key)
            
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=conversation.messages,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,  # Changed to False to simplify error handling
                stop=None,
            )
            
            return completion.choices[0].message.content
        except Exception as api_error:
            print(f"Groq API error: {str(api_error)}")
            error_msg = str(api_error)
            
            if "401" in error_msg or "invalid_api_key" in error_msg:
                return f"Error: Invalid Groq API key. Please update your .env file with a valid Groq API key. Technical details: {error_msg}"
            elif "429" in error_msg:
                return f"Error: The Groq API rate limit has been exceeded. Please try again later. Technical details: {error_msg}"
            else:
                return f"Error communicating with Groq API: {error_msg}"
    
    except Exception as e:
        print(f"Unexpected error in query_groq_api: {str(e)}")
        return f"An unexpected error occurred while processing your request: {str(e)}"


def get_or_create_conversation(conversation_id: str) -> Conversation:
    if conversation_id not in conversations:
        conversations[conversation_id] = Conversation()
    return conversations[conversation_id]

def get_conversation_from_db(db: Session, conversation_id: str, user_id: int):
    # Get or create the conversation in the database
    db_conversation = conv_utils.get_or_create_db_conversation(db, conversation_id, user_id)
    
    # Get all messages
    messages = conv_utils.get_conversation_messages(db, db_conversation.id)
    
    # Format messages for the chat API
    formatted_messages = conv_utils.format_messages_for_chat_api(messages)
    
    # Our desired system message
    desired_system_message = "You are an intelligent AI chatbot designed to have natural conversations. Respond in a helpful and informative way."
    
    # Check if there's a system message already
    system_message_index = None
    for i, msg in enumerate(formatted_messages):
        if msg.get("role") == "system":
            system_message_index = i
            break
    
    if system_message_index is not None:
        # Update the existing system message to our desired one
        old_content = formatted_messages[system_message_index]["content"]
        if old_content != desired_system_message:
            formatted_messages[system_message_index]["content"] = desired_system_message
            
            # Update in database too
            # Find the system message ID
            system_msg_id = None
            for msg in messages:
                if msg.role == "system":
                    system_msg_id = msg.id
                    break
                    
            if system_msg_id:
                # Update directly in database
                from database import Message
                db_msg = db.query(Message).filter(Message.id == system_msg_id).first()
                if db_msg:
                    db_msg.content = desired_system_message
                    db.commit()
    else:
        # No system message, add one
        system_message = {"role": "system", "content": desired_system_message}
        formatted_messages.insert(0, system_message)
        
        # Also add to database for consistency
        conv_utils.add_message_to_conversation(db, db_conversation.id, "system", desired_system_message)
    
    # Create a conversation object
    conversation = Conversation(messages=formatted_messages)
    
    # Add to memory cache
    conversations[conversation_id] = conversation
    
    return conversation, db_conversation


@app.post("/chat/")
async def chat(
    input: UserInput,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    print(f"Chat request received from user {current_user.username}:")
    print(f"  - Message: {input.message}")
    print(f"  - Role: {input.role}")
    print(f"  - Conversation ID: {input.conversation_id}")
    
    # Generate a new conversation ID if not provided
    if not input.conversation_id:
        input.conversation_id = conv_utils.generate_conversation_id()
        print(f"  - Generated new conversation_id: {input.conversation_id}")
    
    # Get or create conversation from database
    try:
        conversation, db_conversation = get_conversation_from_db(
            db, input.conversation_id, current_user.id
        )
        print(f"  - Retrieved conversation with ID: {db_conversation.id}")
    except Exception as e:
        print(f"Error getting conversation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation: {str(e)}"
        )

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
        
        # Add the message to the database
        try:
            conv_utils.add_message_to_conversation(
                db, db_conversation.id, input.role, input.message
            )
        except Exception as db_error:
            print(f"Error adding message to database: {str(db_error)}")
            # Continue with the conversation even if db operation fails
        
        # Get response from Groq API
        response = query_groq_api(conversation)
        
        # Add the assistant's response to the conversation
        conversation.messages.append({
            "role": "assistant",
            "content": response
        })
        
        # Add the assistant's response to the database
        try:
            conv_utils.add_message_to_conversation(
                db, db_conversation.id, "assistant", response
            )
        except Exception as db_error:
            print(f"Error adding assistant response to database: {str(db_error)}")
            # Continue with the conversation even if db operation fails
        
        # Update the conversation title for new conversations
        if len(conversation.messages) == 3:  # system message + user message + assistant response
            try:
                # Use the first part of the user's message as the title
                title = input.message[:50] + ("..." if len(input.message) > 50 else "")
                conv_utils.update_conversation_title(db, input.conversation_id, title)
            except Exception as title_error:
                print(f"Error updating conversation title: {str(title_error)}")
                # This is non-critical, so continue
        
        return {
            "response": response,
            "conversation_id": input.conversation_id
        }
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        # Return a more user-friendly error message
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while processing your message: {str(e)}"
        )
    
# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print(f"Login attempt for username: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        print(f"Login failed: invalid credentials for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    print(f"Login successful for user: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        print(f"🔍 Registration attempt for username: {user.username}")
        db_user = get_user(db, user.username)
        if db_user:
            print(f"⚠️ Username already exists: {user.username}")
            raise HTTPException(
                status_code=400, 
                detail="Username already registered"
            )
        print(f"✅ Creating new user: {user.username}")
        return create_user(db, user)
    except Exception as e:
        print(f"🚨 Registration error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    return current_user

# Conversation management endpoints
@app.get("/conversations/", response_model=ConversationList)
async def get_conversations(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    conversations = conv_utils.get_user_conversations(db, current_user.id)
    return {"conversations": conversations}

@app.get("/conversations/{conversation_id}/messages", response_model=MessageList)
async def get_conversation_messages(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from database import Conversation
    db_conversation = db.query(Conversation).filter(
        Conversation.conversation_id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not db_conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    
    messages = conv_utils.get_conversation_messages(db, db_conversation.id)
    return {"messages": messages}

@app.put("/conversations/{conversation_id}")
async def update_conversation_title(
    conversation_id: str,
    data: dict,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    title = data.get("title")
    if not title:
        raise HTTPException(
            status_code=400,
            detail="Title is required"
        )
    
    db_conversation = conv_utils.update_conversation_title(db, conversation_id, title)
    if not db_conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    
    return {"success": True}

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    success = conv_utils.delete_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )
    
    return {"success": True}

#---------------- function for speech-to-speech # --------------------------

@app.post("/synthesize/")
async def synthesize_speech(data: dict):
    """Convert text to speech using Google's TTS service"""
    try:
        text = data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        print(f"Synthesizing speech for text: {text[:50]}...")
        
        # Create a temporary file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            # Generate speech using gTTS and save to file
            tts = gtts.gTTS(text=text, lang="en", slow=False)
            tts.save(temp_path)
            
            # Read the file content
            with open(temp_path, "rb") as audio_file:
                audio_content = audio_file.read()
                
            # Create BytesIO object
            fp = io.BytesIO(audio_content)
            fp.seek(0)
            
            # Return audio file
            return StreamingResponse(fp, media_type="audio/mpeg")
        finally:
            # Clean up the temporary file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        import traceback
        print(f"Speech synthesis error: {str(e)}")
        print(traceback.format_exc())
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

if __name__ == "__main__":
    # Create database tables before starting
    create_tables()
    
    import uvicorn
    # Using port 8001 to avoid conflicts with any existing servers
    print(f"Starting server with Groq API key: {GROQ_API_KEY[:5]}...{GROQ_API_KEY[-5:]}")
    uvicorn.run(app, host="0.0.0.0", port=8001)