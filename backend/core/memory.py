import os
import sqlite3
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "friday.db")

class MemoryCore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db()
        
    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT CHECK(role IN ('system', 'user', 'assistant', 'tool')) NOT NULL,
                    content TEXT,
                    tool_calls TEXT,
                    tool_call_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create system preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_prefs (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
    def add_message(self, session_id: str, role: str, content: str = None, tool_calls: str = None, tool_call_id: str = None):
        """Save a message to the persistent conversation log."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (session_id, role, content, tool_calls, tool_call_id)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, role, content, tool_calls, tool_call_id))
            conn.commit()
            
    def get_recent_history(self, session_id: str, limit: int = 15) -> List[Dict]:
        """Load conversation context from the database for the LLM."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Fetch latest rows, then reverse to chronological order for the LLM
            cursor.execute("""
                SELECT role, content, tool_calls, tool_call_id
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            rows = cursor.fetchall()
            messages = []
            
            for row in reversed(rows):
                msg = {"role": row["role"]}
                if row["content"] is not None:
                    msg["content"] = row["content"]
                if row["tool_calls"] is not None:
                    import json
                    msg["tool_calls"] = json.loads(row["tool_calls"])
                if row["tool_call_id"] is not None:
                    msg["tool_call_id"] = row["tool_call_id"]
                messages.append(msg)
                
            return messages

    def clear_session(self, session_id: str):
        """Purge memory for a specific session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()

# Simple testing
if __name__ == "__main__":
    mem = MemoryCore()
    mem.add_message("default", "system", "You are F.R.I.D.A.Y")
    mem.add_message("default", "user", "Hello")
    print("Test passed! DB created at:", mem.db_path)
