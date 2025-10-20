# 🧪 Device Isolation Testing Guide

## ⚡ Quick Test (5 minutes)

### Prerequisites
- Backend running on http://localhost:8000
- Frontend running on http://localhost:3001
- Two different browsers (Chrome + Firefox)

---

## 📋 Step-by-Step Test Procedure

### Step 1: Clean Slate Setup

**Stop all servers:**
```bash
# Press Ctrl+C in backend terminal
# Press Ctrl+C in frontend terminal
```

**Delete old database:**
```bash
cd backend
rm data/database/chat_history.db  # Mac/Linux
# OR
del data\database\chat_history.db # Windows PowerShell
```

**Restart servers:**
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

### Step 2: Clear Browser Storage (CRITICAL!)

**In Chrome:**
1. Open http://localhost:3001
2. Press `F12` → **Application** tab
3. Click **Local Storage** → http://localhost:3001
4. Find `pdfpixie_device_id` → **Delete** (if exists)
5. **Close DevTools**
6. **Refresh page** (Ctrl+R)

**In Firefox:**
1. Open http://localhost:3001
2. Press `F12` → **Storage** tab
3. Click **Local Storage** → http://localhost:3001
4. Find `pdfpixie_device_id` → **Delete** (if exists)
5. **Close DevTools**
6. **Refresh page** (Ctrl+R)

---

### Step 3: Test in Browser 1 (Chrome)

1. **Upload a PDF document**
   - Click "Upload PDF" button
   - Select any PDF file
   - Wait for upload to complete

2. **Send test message**
   - Type: `This is from Chrome browser`
   - Press Send

3. **Verify device ID**
   - Press `F12` to open Console
   - Type: `localStorage.getItem('pdfpixie_device_id')`
   - **Copy this device ID** (e.g., `device_1703012345_abc123`)
   - You should see log: `🆔 Using EXISTING device ID: device_...`

4. **Check backend logs**
   - Look at backend terminal
   - Should see: `📥 Received query from ... device device_1703012345_abc123`
   - Should see: `Creating new chat session for document ..., device device_1703012345_abc123`

---

### Step 4: Test in Browser 2 (Firefox)

1. **Open the SAME PDF**
   - Upload the same PDF file you used in Chrome
   - Wait for upload to complete

2. **Check chat history**
   - ✅ **EXPECTED:** Chat should be **EMPTY**
   - ❌ **FAILURE:** If you see "This is from Chrome browser" → Device isolation NOT working

3. **Send different message**
   - Type: `This is from Firefox browser`
   - Press Send

4. **Verify different device ID**
   - Press `F12` to open Console
   - Type: `localStorage.getItem('pdfpixie_device_id')`
   - **This should be DIFFERENT from Chrome's device ID**
   - Example: `device_1703012567_xyz789`

5. **Check backend logs**
   - Should see: `📥 Received query from ... device device_1703012567_xyz789`
   - Should see: `Creating new chat session for document ..., device device_1703012567_xyz789`
   - **Note:** Device ID is different from Chrome!

---

### Step 5: Verify Isolation (Return to Chrome)

1. **Switch back to Chrome browser**
2. **Refresh the page** (Ctrl+R) or reopen the PDF
3. **Check chat history:**
   - ✅ **EXPECTED:** Should see only "This is from Chrome browser"
   - ❌ **FAILURE:** If you see Firefox message → Isolation FAILED

4. **Send another message from Chrome**
   - Type: `Chrome second message`
   - Press Send

---

### Step 6: Final Verification (Return to Firefox)

1. **Switch back to Firefox browser**
2. **Refresh the page** (Ctrl+R) or reopen the PDF
3. **Check chat history:**
   - ✅ **EXPECTED:** Should see only "This is from Firefox browser"
   - ❌ **FAILURE:** If you see Chrome messages → Isolation FAILED

---

## 🔍 Verification Checklist

| Test | Chrome | Firefox | Status |
|------|--------|---------|--------|
| Device ID exists | `device_123_abc` | `device_456_xyz` | ✅ Different |
| First message visible | "This is from Chrome" | "This is from Firefox" | ✅ Separate |
| Other browser's messages hidden | No Firefox messages | No Chrome messages | ✅ Isolated |
| Backend logs show device_id | Yes | Yes | ✅ Received |
| New sessions created per device | Yes | Yes | ✅ Working |

---

## 🐛 Troubleshooting

### Problem: Still seeing shared chat history

**Diagnosis:**
```javascript
// In BOTH browsers, check:
localStorage.getItem('pdfpixie_device_id')

// If same device_id in both browsers → localStorage not cleared properly
// If different device_ids → backend not using device_id for filtering
```

**Solutions:**

1. **Clear localStorage completely:**
   ```javascript
   localStorage.clear()
   location.reload()
   ```

2. **Check backend is receiving device_id:**
   - Look at backend terminal
   - Should see: `device device_123_abc` in logs
   - If you see `device None` → Frontend not sending device_id

3. **Verify backend code updated:**
   ```bash
   cd backend
   grep -n "device_id" main.py
   grep -n "device_id" app/chat_history_db.py
   # Should see multiple matches
   ```

4. **Database has device_id column:**
   ```bash
   cd backend
   python scripts/test_device_isolation.py
   # Should show device_id column exists
   ```

---

### Problem: Backend shows "device None" or "fallback_xxx"

**Cause:** Frontend not sending device_id properly

**Fix:**

1. **Check ChatPanel.tsx imports:**
   ```typescript
   import { getDeviceId } from '../utils/deviceId'
   ```

2. **Check console for device_id logs:**
   ```
   🆔 Using EXISTING device ID: device_123_abc
   🆔 Device ID being sent: device_123_abc
   ✅ Query sent with device_id: device_123_abc
   ```

3. **Restart frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

---

### Problem: "Legacy" label showing on chat sessions

**Cause:** Old sessions without device_id

**Fix:**

1. **Delete old database:**
   ```bash
   cd backend
   rm data/database/chat_history.db
   ```

2. **Restart backend:**
   ```bash
   uvicorn main:socket_app --reload
   ```

3. **Upload NEW PDF and test again**

---

## 🧪 Database Verification

**Run test script:**
```bash
cd backend
python scripts/test_device_isolation.py
```

**Expected output:**
```
============================================================
🧪 DEVICE ID ISOLATION TEST
============================================================

📊 Total sessions in database: 2

🔍 Unique devices: 2

------------------------------------------------------------

📱 Device: device_1703012345_abc123
   Sessions: 1
   - Session 12345678... | Doc: abcdef12... | Messages: 2

📱 Device: device_1703012567_xyz789
   Sessions: 1
   - Session 87654321... | Doc: abcdef12... | Messages: 1

------------------------------------------------------------

✅ All sessions have device_id

📄 Documents with sessions: 1

📄 Document abcdef12...
   Accessed from 2 different devices:
   - device_1703012345_abc123: 1 session(s)
   - device_1703012567_xyz789: 1 session(s)
   ✅ Proper isolation: Each device has separate sessions

============================================================
✅ Device ID isolation test complete!
============================================================
```

---

## ✅ Success Criteria

Your implementation is working correctly when:

1. ✅ **Each browser has unique device_id** in localStorage
2. ✅ **Chrome shows only Chrome messages** (no Firefox messages)
3. ✅ **Firefox shows only Firefox messages** (no Chrome messages)
4. ✅ **Backend logs show device_id** for every query
5. ✅ **Database has separate sessions** per device
6. ✅ **No "Legacy" labels** on new chat sessions
7. ✅ **Test script shows proper isolation**

---

## 🚀 Advanced Testing

### Test 3: Mobile Browser
1. Open app on mobile device: `http://YOUR_IP:3001`
2. Upload same PDF
3. ✅ Should have empty chat (different device)

### Test 4: Incognito/Private Mode
1. Open Chrome Incognito
2. Upload PDF and send message
3. Open regular Chrome
4. ✅ Should NOT see incognito messages (different device_id)

### Test 5: Clear and Restore
1. In Chrome: `localStorage.removeItem('pdfpixie_device_id')`
2. Refresh page
3. ✅ New device_id generated
4. ✅ Chat history resets (new device identity)

---

## 📊 Expected Logs

### Frontend Console (Chrome):
```
🆔 Generated NEW device ID: device_1703012345_abc123
📤 Sending query to backend: {...}
🆔 Device ID being sent: device_1703012345_abc123
✅ Query sent with device_id: device_1703012345_abc123
```

### Backend Terminal:
```
📥 Received query from abc123: This is from Chrome... device device_1703012345_abc123
Creating new chat session for document doc-xyz, device device_1703012345_abc123
💾 Saved user message to session session-123
✅ Generated response for abc123: ...
```

---

## 📝 Notes

- **Same browser tabs** share same device_id (expected)
- **Different browsers** have different device_ids ✅
- **Private mode** generates new device_id each session
- **Clearing localStorage** removes device_id → new identity
- **Database persists** device_id for session history

---

**Test Duration:** ~5 minutes  
**Required:** 2 browsers + PDF file  
**Result:** Confirmed device-specific chat isolation ✅
