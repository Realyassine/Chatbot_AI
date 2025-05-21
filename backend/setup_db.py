import os
from dotenv import load_dotenv
import sqlite3
from sqlalchemy import create_engine
from database import Base

# Load environment variables
load_dotenv()

def setup_db():
    """Set up the database based on the DATABASE_URL in .env"""
    print("Setting up database...")
    
    # Get database URL from .env or use SQLite as default
    db_url = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
    
    if db_url.startswith("sqlite"):
        print("Using SQLite database")
        # Extract the file path
        db_path = db_url.replace("sqlite:///", "")
        
        # Check if the database file exists
        if os.path.exists(db_path):
            print(f"Database already exists at {db_path}")
        else:
            print(f"Creating new database at {db_path}")
            # Create an empty file
            conn = sqlite3.connect(db_path)
            conn.close()
    
    elif db_url.startswith("mysql"):
        print("Using MySQL database")
        print("Note: Make sure your MySQL server is running")
        # MySQL-specific checks could be added here
    
    else:
        print(f"Unknown database type in URL: {db_url}")
    
    # Create tables using SQLAlchemy models
    try:
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        print("Falling back to SQLite...")
        
        # Update the DATABASE_URL in the .env file
        env_path = ".env"
        with open(env_path, "r") as f:
            lines = f.readlines()
        
        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith("DATABASE_URL"):
                    f.write("DATABASE_URL = sqlite:///./chatbot.db\n")
                else:
                    f.write(line)
        
        # Try again with SQLite
        engine = create_engine("sqlite:///./chatbot.db")
        Base.metadata.create_all(engine)
        print("Database tables created successfully with SQLite fallback")
    
    print("Database setup complete")

if __name__ == "__main__":
    setup_db()