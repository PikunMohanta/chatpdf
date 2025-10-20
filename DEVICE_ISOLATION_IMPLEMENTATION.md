# Device-Specific Chat History Implementation

## Problem
Chat history was appearing across all devices and browsers because all sessions used the same `user_id = "anonymous"`. This caused privacy and confusion issues when users accessed the app from different devices.

## Solution
Implemented device-specific chat history isolation using unique device identifiers stored in browser localStorage.

---

## Changes Made

### 1. Database Schema Update
**File:** `backend/app/database.py`

- **Added `device_id` column** to `ChatSessionDB` model
- Kept `user_id` for backward compatibility
- New field: `device_id = Column(String(100), nullable=True, index=True)`

```python
class ChatSessionDB(Base):
    session_id = Column(String(36), primary_key=True, index=True)
    document_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)  # Kept for compatibility
    device_id = Column(String(100), nullable=True, index=True)  # NEW: Device isolation
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### 2. Chat History Manager Updates
**File:** `backend/app/chat_history_db.py`

#### Updated Classes:
- **ChatSession class**: Added `device_id` parameter to `__init__`, `to_dict`, `from_dict`, and `from_db` methods

#### Updated Methods:
1. **`create_session(document_id, user_id=None, device_id=None)`**
   - Now accepts optional `device_id` parameter
   - Stores device_id in database
   - Logs device_id for debugging

2. **`get_document_sessions(document_id, user_id=None, device_id=None)`**
   - Prioritizes `device_id` filtering for isolation
   - Falls back to `user_id` for legacy sessions
   - Excludes legacy sessions when device_id is provided

3. **`get_latest_session_for_document(document_id, user_id=None, device_id=None)`**
   - Filters by `device_id` first, then `user_id`
   - Returns None if neither is provided

### 3. Socket.IO Backend Handler
**File:** `backend/main.py`

Updated `query` event handler:
- Extracts `device_id` from incoming socket data
- Logs warning if device_id is missing
- Passes `device_id` to `create_session` method
- Improved logging to show device_id in messages

```python
@sio.event
async def query(sid, data):
    device_id = data.get('device_id')  # NEW: Get device_id
    
    if not device_id:
        logger.warning(f"⚠️  No device_id provided - chat history may not be properly isolated")
    
    session = chat_history_manager.create_session(document_id, user_id=user_id, device_id=device_id)
```

### 4. Frontend Device ID Utility
**File:** `frontend/src/utils/deviceId.ts` (NEW)

Created utility module with:
- **`getDeviceId()`**: Gets or generates unique device ID
- **`clearDeviceId()`**: Clears device ID for testing
- **`getDeviceInfo()`**: Returns device ID info for debugging

Device ID format: `device_<timestamp>_<random>`

```typescript
export function getDeviceId(): string {
  let deviceId = localStorage.getItem('pdfpixie_device_id');
  
  if (!deviceId) {
    deviceId = generateDeviceId();
    localStorage.setItem('pdfpixie_device_id', deviceId);
  }
  
  return deviceId;
}
```

### 5. Frontend Socket Communication
**File:** `frontend/src/components/ChatPanel.tsx`

- Imported `getDeviceId` utility
- Called `getDeviceId()` before sending query
- Added `device_id` to socket.emit payload

```typescript
const deviceId = getDeviceId();

socket.emit('query', {
  document_id: documentId,
  query: queryText,
  session_id: currentSessionId,
  user_id: 'anonymous',  // Legacy support
  device_id: deviceId,   // NEW: Device isolation
})
```

---

## How It Works

### Device ID Generation
1. On first visit, frontend generates unique device ID: `device_1234567890_abc123`
2. Device ID stored in browser's localStorage
3. Same device ID used for all subsequent chats on this browser

### Chat History Isolation
1. **User opens PDF on Chrome Desktop**
   - Device ID: `device_123_abc`
   - Creates session with this device_id
   - All messages saved with this device_id

2. **User opens same PDF on Firefox**
   - Device ID: `device_456_def` (different!)
   - Creates new session with different device_id
   - Shows empty chat history (properly isolated)

3. **User returns to Chrome**
   - Same device ID: `device_123_abc`
   - Loads previous chat history from this device
   - No messages from Firefox appear

### Database Query Flow
```python
# Backend filters sessions by device_id
sessions = db.query(ChatSessionDB).filter(
    ChatSessionDB.document_id == document_id,
    ChatSessionDB.device_id == device_id  # Only this device's chats
).all()
```

---

## Testing Instructions

### Test 1: Device Isolation
1. **Open app in Chrome**
   - Upload PDF and send messages
   - Note chat history appears

2. **Open app in Firefox (same computer)**
   - Open same PDF
   - Verify: Chat history is EMPTY (isolated)

3. **Return to Chrome**
   - Open same PDF
   - Verify: Previous chat history appears (persistent)

### Test 2: Clear Device ID
```javascript
// Open browser console
localStorage.removeItem('pdfpixie_device_id')
location.reload()
// New device ID generated, chat history resets
```

### Test 3: Check Database
```sql
SELECT session_id, document_id, device_id, created_at 
FROM chat_sessions 
ORDER BY created_at DESC;

-- Each device should have unique device_id
-- Legacy sessions may have device_id = NULL
```

---

## Migration Notes

### Existing Data
- Old sessions have `device_id = NULL`
- Backend includes legacy support for backward compatibility
- Old sessions still accessible via `user_id` filtering

### Fresh Start (Recommended)
To start clean without legacy data:
```bash
# Delete existing database
rm backend/data/database/chat_history.db

# Restart backend - database will be recreated with new schema
```

### Migration Script (Optional)
If you want to preserve existing sessions:
```python
# Assign dummy device_ids to existing sessions
from app.database import get_db_session, ChatSessionDB
import uuid

db = get_db_session()
sessions = db.query(ChatSessionDB).filter(ChatSessionDB.device_id.is_(None)).all()

for session in sessions:
    session.device_id = f"legacy_device_{uuid.uuid4()}"
    
db.commit()
```

---

## Backward Compatibility

### Legacy Support Features
1. **`user_id` still exists** in database (not removed)
2. **Methods accept both** `user_id` and `device_id`
3. **Priority system**: device_id first, user_id fallback
4. **Legacy sessions** (device_id=NULL) still queryable via user_id

### Deprecation Path
1. **Phase 1** (Current): Both user_id and device_id supported
2. **Phase 2** (Future): Migrate all sessions to device_id
3. **Phase 3** (Future): Remove user_id column entirely

---

## Benefits

✅ **Privacy**: Chat history isolated per device/browser  
✅ **Clarity**: No confusion from other devices' chats  
✅ **Persistent**: Each device maintains its own history  
✅ **Backward Compatible**: Old sessions still work  
✅ **Simple**: Automatic device ID management via localStorage  
✅ **Testable**: Easy to clear and reset device identity  

---

## Troubleshooting

### Issue: Chat history still appearing across devices
- Check browser console for device_id in logs
- Verify device_id is different on each browser
- Check backend logs show device_id being received
- Ensure database schema has device_id column

### Issue: Lost chat history after clearing browser data
- Expected behavior: localStorage cleared = new device_id = new history
- To preserve: Don't clear localStorage or export chat history

### Issue: Private browsing mode
- localStorage may not persist across sessions
- New device_id generated each time in private mode
- Consider cookie-based fallback for private browsing

---

## Files Modified

### Backend
- ✅ `backend/app/database.py` - Added device_id column
- ✅ `backend/app/chat_history_db.py` - Updated all methods
- ✅ `backend/main.py` - Updated socket handler

### Frontend
- ✅ `frontend/src/utils/deviceId.ts` - NEW utility file
- ✅ `frontend/src/components/ChatPanel.tsx` - Send device_id

### Documentation
- ✅ `DEVICE_ISOLATION_IMPLEMENTATION.md` - This file

---

## Next Steps (Optional Enhancements)

1. **User Authentication**: Replace device_id with actual user accounts
2. **Cross-Device Sync**: Allow users to sync history across their devices
3. **Export/Import**: Let users export and import chat history
4. **Device Management**: UI to view and manage registered devices
5. **Session Sharing**: Option to share specific chat sessions across devices

---

## Conclusion

The implementation successfully isolates chat history per device using browser localStorage. Each device maintains its own independent chat history while remaining backward compatible with existing sessions. The solution is simple, effective, and requires no user configuration.
