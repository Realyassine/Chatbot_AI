"""
Script to clean test conversations
"""
import sqlite3

def clean_db():
    try:
        conn = sqlite3.connect('chatbot.db')
        cursor = conn.cursor()
        
        print("Cleaning test conversations...")
        # Delete test messages
        cursor.execute('DELETE FROM messages WHERE content LIKE "%system instructions%"')
        conn.commit()
        print(f"Deleted {cursor.rowcount} messages with 'system instructions'")
        
        # Update all system messages
        cursor.execute(
            "UPDATE messages SET content = ? WHERE role = 'system'",
            ("You are an intelligent AI chatbot designed to have natural conversations. Respond in a helpful and informative way.",)
        )
        conn.commit()
        print(f"Updated {cursor.rowcount} system messages")
        
        conn.close()
        print("Database cleaned")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    clean_db()
