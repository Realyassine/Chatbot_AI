from sqlalchemy.orm import Session
from database import Conversation as DBConversation, Message
from typing import List, Dict, Optional
from pydantic import BaseModel, field_serializer
import uuid
from datetime import datetime

class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    # Add serializers for datetime fields
    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info):
        return dt.isoformat()
    
    @field_serializer('updated_at')
    def serialize_updated_at(self, dt: datetime, _info):
        return dt.isoformat()

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
    
    # Add serializer for timestamp field
    @field_serializer('timestamp')
    def serialize_timestamp(self, dt: datetime, _info):
        return dt.isoformat()

# Get or create a conversation in the database
def get_or_create_db_conversation(db: Session, conversation_id: str, user_id: int):
    db_conversation = db.query(DBConversation).filter(
        DBConversation.conversation_id == conversation_id
    ).first()
    
    if not db_conversation:
        db_conversation = DBConversation(
            conversation_id=conversation_id,
            user_id=user_id
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        
        # Add system message
        system_message = Message(
            conversation_id=db_conversation.id,
            role="system",
            content="You are a useful AI assistant."
        )
        db.add(system_message)
        db.commit()
    
    return db_conversation

# Add a message to a conversation
def add_message_to_conversation(db: Session, db_conversation_id: int, role: str, content: str):
    message = Message(
        conversation_id=db_conversation_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Update the conversation's updated_at timestamp
    db_conversation = db.query(DBConversation).filter(
        DBConversation.id == db_conversation_id
    ).first()
    db.commit()
    
    return message

# Get all messages for a conversation
def get_conversation_messages(db: Session, db_conversation_id: int):
    return db.query(Message).filter(
        Message.conversation_id == db_conversation_id
    ).order_by(Message.timestamp).all()

# Get all conversations for a user
def get_user_conversations(db: Session, user_id: int):
    return db.query(DBConversation).filter(
        DBConversation.user_id == user_id
    ).order_by(DBConversation.updated_at.desc()).all()

# Generate a new conversation ID
def generate_conversation_id():
    return str(uuid.uuid4())

# Format messages for the chat API
def format_messages_for_chat_api(messages: List[Message]):
    return [{"role": msg.role, "content": msg.content} for msg in messages]

# Update conversation title
def update_conversation_title(db: Session, conversation_id: str, title: str):
    db_conversation = db.query(DBConversation).filter(
        DBConversation.conversation_id == conversation_id
    ).first()
    
    if db_conversation:
        db_conversation.title = title
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    
    return None

# Delete a conversation
def delete_conversation(db: Session, conversation_id: str, user_id: int):
    db_conversation = db.query(DBConversation).filter(
        DBConversation.conversation_id == conversation_id,
        DBConversation.user_id == user_id
    ).first()
    
    if db_conversation:
        db.delete(db_conversation)  # This will cascade delete all messages
        db.commit()
        return True
    
    return False
