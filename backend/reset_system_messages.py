"""
Script to clean up the database and reset system messages
"""

import sqlite3

def reset_system_messages():
    try:
        print("Connecting to the database...")
        # Connect to the database
        conn = sqlite3.connect('chatbot.db')
        cursor = conn.cursor()
        
        # Find all system messages
        print("Looking for system messages...")
        cursor.execute("SELECT id, role, content FROM messages WHERE role = 'system'")
        system_messages = cursor.fetchall()
        
        print(f"Found {len(system_messages)} system messages")
        for msg_id, role, content in system_messages:
            print(f"ID {msg_id}: {content}")
        
        # Update all system messages with our new version
        new_system_message = "You are an intelligent AI chatbot designed to have natural conversations. Respond in a helpful and informative way."
        print(f"\nUpdating system messages to: {new_system_message}")
        
        cursor.execute(
            "UPDATE messages SET content = ? WHERE role = 'system'",
            (new_system_message,)
        )
        
        # Commit changes and close connection
        conn.commit()
        print(f"Updated {cursor.rowcount} system messages")
        
        # Verify the changes
        cursor.execute("SELECT id, content FROM messages WHERE role = 'system'")
        updated_messages = cursor.fetchall()
        print("\nVerifying updates:")
        for msg_id, content in updated_messages:
            print(f"ID {msg_id}: {content}")
        
        conn.close()
        print("\nDatabase update complete!")
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")

if __name__ == "__main__":
    reset_system_messages()
