# Device-Specific Chat History - Quick Start Guide

## 🎯 What Changed?

Your chat app now isolates chat history **per device/browser**. Each device gets its own independent chat history.

### Before:
- All devices shared the same chat history
- Chat from your phone appeared on your laptop
- Chat from Chrome appeared in Firefox

### After:
- Each browser/device has its own isolated chat history  
- Chrome history ≠ Firefox history ≠ Phone history
- Privacy and clarity improved ✅

---

## 🚀 Quick Setup

### Option 1: Fresh Start (Recommended)

```bash
# Navigate to backend directory
cd backend

# Delete old database
rm data/database/chat_history.db  # Linux/Mac
# OR
del data\database\chat_history.db  # Windows

# Restart backend - database recreates automatically
python -m uvicorn main:socket_app --reload
```

### Option 2: Migration Script (Preserve Data)

```bash
# Navigate to backend directory
cd backend

# Run migration script
python scripts/migrate_device_id.py

# Choose option 2 to migrate existing sessions
```

---

## 🧪 Testing

### Test Device Isolation

1. **Open app in Chrome**
   ```
   Open http://localhost:5173
   Upload a PDF
   Send messages: "Hello from Chrome"
   ```

2. **Open app in Firefox**
   ```
   Open http://localhost:5173
   Open same PDF
   ✅ Chat history should be EMPTY (different device)
   Send messages: "Hello from Firefox"
   ```

3. **Return to Chrome**
   ```
   Open same PDF
   ✅ Should see "Hello from Chrome" (not Firefox messages)
   ```

### Check Device ID

Open browser console:
```javascript
// View your device ID
localStorage.getItem('pdfpixie_device_id')
// Output: "device_1234567890_abc123"

// Clear device ID (start fresh)
localStorage.removeItem('pdfpixie_device_id')
location.reload()
```

---

## 📝 How It Works

### Frontend
1. Generates unique device ID on first visit
2. Stores in browser's localStorage
3. Sends device ID with every chat message

### Backend
1. Receives device ID from frontend
2. Stores with session in database
3. Filters chat history by device ID

### Database
```sql
-- New column added to chat_sessions table
device_id VARCHAR(100)  -- e.g., "device_1234567890_abc123"
```

---

## 🔧 Configuration

### Device ID Format
```typescript
// Generated format
device_<timestamp>_<random>

// Example
device_1703012345_a1b2c3d4e5
```

### Storage Location
- **Frontend**: `localStorage['pdfpixie_device_id']`
- **Backend**: SQLite database `chat_sessions.device_id` column

---

## 📂 Files Modified

### Backend Changes
```
backend/
├── app/
│   ├── database.py             ✏️  Added device_id column
│   ├── chat_history_db.py      ✏️  Updated all methods
│   └── main.py                 ✏️  Socket handler updated
└── scripts/
    └── migrate_device_id.py    ✨  NEW migration script
```

### Frontend Changes
```
frontend/
└── src/
    ├── utils/
    │   └── deviceId.ts         ✨  NEW device ID utility
    └── components/
        └── ChatPanel.tsx        ✏️  Send device_id in messages
```

---

## 🐛 Troubleshooting

### Problem: Chat history still shared across devices

**Check 1: Device IDs are different**
```javascript
// In Chrome console
localStorage.getItem('pdfpixie_device_id')
// Output: device_123_abc

// In Firefox console
localStorage.getItem('pdfpixie_device_id')
// Output: device_456_def  ✅ Should be different!
```

**Check 2: Backend receiving device_id**
```bash
# Check backend logs for:
📥 Received query from <sid>: ... device device_123_abc
```

**Check 3: Database has device_id column**
```bash
cd backend
python scripts/migrate_device_id.py
# Choose option 3 (Show Status)
```

### Problem: Lost chat history after clearing browser data

✅ **Expected behavior** - Clearing localStorage removes device ID, creating new identity.

To preserve history:
- Don't clear browser data
- Backup device ID before clearing
- Use export/import feature (future enhancement)

### Problem: Private browsing mode

⚠️ localStorage may not persist in private/incognito mode.
- New device ID generated each session
- Chat history resets on close
- Consider server-side sessions for private mode

---

## 📊 Database Migration Status

Run this to check migration status:

```bash
cd backend
python scripts/migrate_device_id.py
# Choose option 3: Show Status

# Example output:
# ✅ device_id column exists: Yes
# Total sessions: 15
#   With device_id: 15
#   Without device_id: 0
# ✅ All sessions have device_id
```

---

## 🎓 Advanced Usage

### Export Device ID (for backup)
```javascript
const deviceId = localStorage.getItem('pdfpixie_device_id');
console.log('My device ID:', deviceId);
// Save this ID somewhere safe
```

### Restore Device ID (from backup)
```javascript
const savedDeviceId = 'device_1234567890_abc123';
localStorage.setItem('pdfpixie_device_id', savedDeviceId);
location.reload();
// Your old chat history appears!
```

### View All Device Sessions (SQL)
```sql
-- Connect to SQLite database
sqlite3 backend/data/database/chat_history.db

-- View all sessions grouped by device
SELECT 
    device_id,
    COUNT(*) as session_count,
    MAX(updated_at) as last_used
FROM chat_sessions
GROUP BY device_id;
```

---

## 🚀 Next Steps (Optional)

Want to enhance further? Consider:

1. **User Accounts**: Replace device ID with user authentication
2. **Cross-Device Sync**: Sync chat across user's devices
3. **Device Management**: UI to manage registered devices
4. **Session Export**: Export chat history as JSON/PDF
5. **Session Sharing**: Share specific chats with others

---

## 📚 Documentation

For complete technical details, see:
- `DEVICE_ISOLATION_IMPLEMENTATION.md` - Full implementation guide
- `backend/scripts/migrate_device_id.py` - Migration script code
- `frontend/src/utils/deviceId.ts` - Device ID utility code

---

## ✅ Verification Checklist

Before deploying:

- [ ] Backend updated with device_id column
- [ ] Database migrated (fresh start or migration script)
- [ ] Frontend sending device_id in socket events
- [ ] Tested in 2+ different browsers
- [ ] Chat history properly isolated
- [ ] Backend logs show device_id
- [ ] No errors in browser console
- [ ] Old sessions still accessible (if migrated)

---

## 🤝 Support

Issues? Check:
1. Backend logs for errors
2. Browser console for device_id
3. Database migration status
4. GitHub issues (if applicable)

---

**Implementation Complete! 🎉**

Your chat app now has proper device-specific chat history isolation.
