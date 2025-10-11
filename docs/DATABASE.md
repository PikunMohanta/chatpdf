# Database Implementation for Chat History

## Overview

The chat history system has been migrated from JSON file storage to **SQLite database** using **SQLAlchemy ORM**. This provides better performance, data integrity, and scalability.

## Database Schema

### Tables

#### `chat_sessions`
Stores chat session metadata.

| Column | Type | Description |
|--------|------|-------------|
| `session_id` | VARCHAR(36) | Primary key, UUID |
| `document_id` | VARCHAR(36) | Foreign key to document |
| `user_id` | VARCHAR(100) | User identifier |
| `created_at` | DATETIME | Session creation timestamp |
| `updated_at` | DATETIME | Last update timestamp |

#### `chat_messages`
Stores individual messages in chat sessions.

| Column | Type | Description |
|--------|------|-------------|
| `message_id` | VARCHAR(36) | Primary key, UUID |
| `session_id` | VARCHAR(36) | Foreign key to chat_sessions |
| `text` | TEXT | Message content |
| `sender` | VARCHAR(10) | 'user' or 'ai' |
| `timestamp` | DATETIME | Message timestamp |
| `sources` | TEXT | JSON string of sources (optional) |

### Relationships

- **One-to-Many**: Each `ChatSession` has many `ChatMessages`
- **Cascade Delete**: Deleting a session automatically deletes all its messages

## File Structure

```
backend/
├── app/
│   ├── database.py           # Database configuration, models, session management
│   ├── chat_history_db.py    # Database-backed ChatHistoryManager
│   ├── chat_history.py       # OLD: JSON file-based (kept for reference)
│   └── chat.py               # Updated to use database
├── data/
│   ├── database/
│   │   └── chat_history.db   # SQLite database file (auto-created)
│   └── chat_history/         # OLD: JSON files (can be deleted)
└── main.py                   # Database initialization on startup
```

## Key Features

### 1. **Automatic Database Creation**
- Database tables are created automatically on first run
- No manual migration needed for initial setup
- Database file: `backend/data/database/chat_history.db`

### 2. **Same Interface**
- `ChatHistoryManager` maintains the same API as before
- No changes needed in existing code
- Seamless migration from JSON to database

### 3. **Better Performance**
- Indexed queries for fast lookups
- Efficient filtering and sorting
- Handles large numbers of sessions and messages

### 4. **Data Integrity**
- Foreign key constraints
- Cascade deletes
- Transaction support (rollback on errors)

### 5. **Easy to Query**
```python
# Get all sessions for a user
sessions = chat_history_manager.get_all_user_sessions("user123")

# Get specific session with messages
session = chat_history_manager.get_session("session-uuid")

# Add message to session
chat_history_manager.add_message_to_session(session_id, message)

# Delete session (and all messages)
chat_history_manager.delete_session(session_id)
```

## Migration from JSON Files

### Automatic Migration (if needed)
If you have existing JSON files and want to migrate them to the database:

```python
from app.chat_history import chat_history_manager as old_manager
from app.chat_history_db import chat_history_manager as new_manager
import os
import glob

# Migrate all JSON sessions to database
json_files = glob.glob("./data/chat_history/session_*.json")
for json_file in json_files:
    session_id = os.path.basename(json_file).replace("session_", "").replace(".json", "")
    
    # Load from old JSON
    old_session = old_manager.get_session(session_id)
    if not old_session:
        continue
    
    # Create in new database
    new_session = new_manager.create_session(
        old_session.document_id,
        old_session.user_id
    )
    
    # Add all messages
    for message in old_session.messages:
        new_manager.add_message_to_session(new_session.session_id, message)
    
    print(f"Migrated session {session_id}")
```

### Clean Up Old Files
After migration, you can safely delete the JSON files:
```bash
rm -rf backend/data/chat_history/session_*.json
```

## Database Management

### View Database Contents
```bash
# Install SQLite tools
# Windows: Download from https://www.sqlite.org/download.html
# Linux: sudo apt-get install sqlite3
# Mac: brew install sqlite3

# Open database
sqlite3 backend/data/database/chat_history.db

# View tables
.tables

# View sessions
SELECT * FROM chat_sessions;

# View messages
SELECT * FROM chat_messages;

# Exit
.quit
```

### Backup Database
```bash
# Simple file copy
cp backend/data/database/chat_history.db backup/chat_history_backup.db

# Or use SQLite dump
sqlite3 backend/data/database/chat_history.db .dump > chat_history_backup.sql
```

### Reset Database
```bash
# Delete database file (will be recreated on next run)
rm backend/data/database/chat_history.db
```

## Production Considerations

### For Production Deployment

1. **Use PostgreSQL** (recommended for production):
   ```python
   # In database.py, change DATABASE_URL to:
   DATABASE_URL = "postgresql://user:password@localhost/chatpdf"
   ```

2. **Add Database Migrations** with Alembic:
   ```bash
   # Initialize Alembic
   alembic init alembic
   
   # Create migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migration
   alembic upgrade head
   ```

3. **Connection Pooling**:
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True
   )
   ```

4. **Environment-based Configuration**:
   ```python
   import os
   DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/database/chat_history.db")
   ```

## Advantages Over JSON Files

| Feature | JSON Files | SQLite Database |
|---------|-----------|-----------------|
| **Performance** | Slow for many files | Fast indexed queries |
| **Concurrent Access** | File locking issues | Built-in locking |
| **Data Integrity** | Manual validation | Foreign keys, constraints |
| **Querying** | Load entire file | Efficient SQL queries |
| **Scalability** | Limited | Thousands of sessions |
| **Transactions** | No | Yes, with rollback |
| **Backup** | Copy all files | Single file |

## Testing

```bash
# Start backend
cd backend
uvicorn main:socket_app --reload

# Check logs for:
# "Database initialized successfully"
# "Chat history manager initialized with SQLite database"

# Send a message via frontend
# Check database:
sqlite3 backend/data/database/chat_history.db "SELECT * FROM chat_sessions;"
sqlite3 backend/data/database/chat_history.db "SELECT * FROM chat_messages;"
```

## Troubleshooting

### Database Locked Error
```
sqlite3.OperationalError: database is locked
```
**Solution**: SQLite is single-writer. Make sure:
- Close all database connections properly
- Use `check_same_thread=False` (already configured)
- For high concurrency, migrate to PostgreSQL

### Missing Tables
```
sqlalchemy.exc.OperationalError: no such table: chat_sessions
```
**Solution**: Tables not created. Check:
- `init_db()` is called in main.py
- Database directory exists and is writable
- No errors during startup

### Migration Issues
**Solution**: Delete database and start fresh (dev only):
```bash
rm backend/data/database/chat_history.db
# Restart server - tables will be recreated
```

## API Compatibility

All existing API endpoints work without changes:
- ✅ `GET /api/chat/history/{session_id}` - Get session with messages
- ✅ `GET /api/chat/sessions/all` - Get all user sessions
- ✅ `GET /api/chat/sessions/{document_id}` - Get document sessions
- ✅ `POST /api/chat/query` - Send message (saves to database)
- ✅ Socket.IO `query` event - Real-time chat (saves to database)

## Summary

✅ **Implemented**: SQLite database with SQLAlchemy ORM  
✅ **Tables**: `chat_sessions`, `chat_messages`  
✅ **Auto-init**: Database created on startup  
✅ **Compatible**: Same API as before  
✅ **Tested**: Ready for use  

Your chat history is now stored in a proper database! 🎉
