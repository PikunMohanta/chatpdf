# Testing Device-Specific Chat History

## ✅ Backend and Frontend Restarted

Your servers are now running with the updated device_id code:
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3001 (or check your terminal for the actual port)

---

## 🧪 How to Test Device Isolation

### Step 1: Clear Browser Storage (IMPORTANT!)

Before testing, you MUST clear your browser's localStorage to remove old sessions:

#### In Chrome:
1. Press `F12` to open DevTools
2. Go to **Application** tab
3. Click **Local Storage** → `http://localhost:3001`
4. Right-click → **Clear**
5. **Refresh the page** (F5)

#### In Firefox:
1. Press `F12` to open DevTools
2. Go to **Storage** tab
3. Click **Local Storage** → `http://localhost:3001`
4. Right-click → **Delete All**
5. **Refresh the page** (F5)

### Step 2: Test in First Browser (Chrome)

1. Open http://localhost:3001 in Chrome
2. Upload a PDF document
3. Send a message: "Hello from Chrome"
4. Open DevTools Console (F12)
5. Type: `localStorage.getItem('pdfpixie_device_id')`
6. **Note this device ID** (e.g., `device_1234567890_abc123`)

### Step 3: Test in Second Browser (Firefox)

1. Open http://localhost:3001 in Firefox
2. Open the **same PDF document**
3. **VERIFY:** Chat history should be **EMPTY** ✅
4. Send a message: "Hello from Firefox"
5. Open DevTools Console (F12)
6. Type: `localStorage.getItem('pdfpixie_device_id')`
7. **Verify:** This device ID is **DIFFERENT** from Chrome's ✅

### Step 4: Return to Chrome

1. Switch back to Chrome browser
2. Open the same PDF document
3. **VERIFY:** You should see only "Hello from Chrome" ✅
4. **VERIFY:** You should NOT see "Hello from Firefox" ✅

---

## 🔍 What to Check

### Backend Logs
Your backend should show device_id in logs:

```
📥 Received query from <sid>: Hello from Chrome... for document abc123, session xyz, device device_1234567890_abc
```

Look for the `device device_123_abc` part!

### Frontend Console
Check browser console (F12):

```javascript
localStorage.getItem('pdfpixie_device_id')
// Should show: "device_1234567890_abc123"
```

Each browser should have a **different device ID**.

---

## ❌ Troubleshooting

### Problem: Still seeing shared chat history

**Solution 1: Clear localStorage completely**
```javascript
// In browser console (F12)
localStorage.clear()
location.reload()
```

**Solution 2: Clear browser cache**
- Chrome: Ctrl+Shift+Delete → Select "Cached images and files" and "Cookies and other site data"
- Firefox: Ctrl+Shift+Delete → Select "Cookies" and "Cache"

**Solution 3: Check backend logs**
```
# Backend terminal should show:
Creating new chat session for document <id>, device device_123_abc
```

If you see `device unknown` or `device None`, the frontend isn't sending device_id properly.

### Problem: Backend errors

Check backend terminal for errors related to:
- `device_id` column not found → Database needs to be recreated
- SQLAlchemy errors → Database schema mismatch

**Fix:** Delete database and let it recreate:
```bash
# Stop backend (Ctrl+C in backend terminal)
cd backend
rm data/database/chat_history.db   # Linux/Mac
# OR
del data\database\chat_history.db  # Windows

# Restart backend
uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
```

### Problem: PDF showing UUID instead of name

This happens when:
1. Old sessions without proper document metadata
2. Legacy sessions being loaded

**Fix:** Upload a new PDF document and test with that. Old sessions may have incomplete metadata.

---

## 🎯 Expected Results

✅ **Chrome device ID:** `device_1234567890_abc123`  
✅ **Firefox device ID:** `device_9876543210_xyz789`  
✅ **Chrome sees:** Only Chrome messages  
✅ **Firefox sees:** Only Firefox messages  
✅ **Backend logs:** Show different device_ids  
✅ **No cross-device:** Chat history properly isolated  

---

## 📊 Database Verification (Optional)

Want to see the data in the database?

```bash
cd backend
sqlite3 data/database/chat_history.db

# Check sessions with device_id
SELECT session_id, document_id, device_id, created_at 
FROM chat_sessions 
ORDER BY created_at DESC;

# You should see different device_ids for different browsers!
```

---

## 🔄 Start Fresh (If Needed)

If you want to completely reset everything:

```bash
# 1. Clear browser localStorage in ALL browsers
localStorage.clear()

# 2. Stop backend (Ctrl+C)

# 3. Delete database
cd backend
rm data/database/chat_history.db  # Linux/Mac
del data\database\chat_history.db # Windows

# 4. Restart backend
uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000

# 5. Restart frontend
cd frontend
npm run dev

# 6. Refresh browsers (F5)
```

---

## ✨ Success Criteria

Your implementation is working correctly when:

1. ✅ Each browser has unique device_id in localStorage
2. ✅ Chrome shows only Chrome messages
3. ✅ Firefox shows only Firefox messages
4. ✅ Backend logs show device_id values
5. ✅ No "Legacy" label appears for new chats
6. ✅ PDF name appears correctly (not UUID)

---

## 🎉 Next Steps After Verification

Once you've confirmed device isolation is working:

1. Document the device_id format for your team
2. Consider adding device management UI (optional)
3. Test on mobile browsers (different devices)
4. Consider user authentication (future enhancement)
5. Add session export/import features (future)

---

## 📝 Notes

- **Device ID persists** across browser sessions (stored in localStorage)
- **Clearing browser data** removes device ID → new identity
- **Private/Incognito mode** may not persist device ID
- **Each browser tab** shares the same device ID (same browser)
- **Different browsers** have different device IDs ✅

---

**Current Status:** Backend and frontend restarted with device_id support. Ready for testing!
