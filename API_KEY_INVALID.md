# 🔑 OpenRouter API Key Issue - SOLUTION

## ❌ Problem Confirmed

Your OpenRouter API key is **INVALID** (HTTP 401 error).

```
API Key: sk-or-v1-0d1570...52a701b711
Status: 401 Unauthorized
```

This is why you've been getting mock responses!

## ✅ Solution: Get a New API Key

### Step 1: Visit OpenRouter
Go to: **https://openrouter.ai/keys**

### Step 2: Sign In / Sign Up
- If you don't have an account, create one
- Sign in with Google, GitHub, or email

### Step 3: Generate New API Key
1. Click **"Create Key"** or **"New Key"**
2. Give it a name (e.g., "Newchat Development")
3. Copy the key (starts with `sk-or-v1-...`)

### Step 4: Update Your `.env` File
Open: `backend/.env`

Replace the old key:
```env
# OLD (invalid)
OPENROUTER_API_KEY=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

# NEW (your new key)
OPENROUTER_API_KEY=sk-or-v1-YOUR-NEW-KEY-HERE
```

### Step 5: Restart Backend
```powershell
cd backend
uv run uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Test Again
```powershell
python test_openrouter_no_deps.py
```

You should see:
```
✅ SUCCESS! OpenRouter is working!
🤖 AI Response:
   OpenRouter is working!
```

## 💰 OpenRouter Pricing

OpenRouter is **pay-as-you-go**:
- You need to add credits to your account
- Visit: https://openrouter.ai/account
- Add at least $5 to start

### Free Tier
Some models have free tiers, but the model we're using (`llama-3.1-8b-instruct`) requires credits.

### Alternative: Free Models
Edit `backend/app/openrouter_client.py` to use a free model:

```python
def chat_completion(
    self, 
    messages: List[Dict[str, str]], 
    model: str = "google/gemini-flash-1.5-8b",  # ← Free model
    max_tokens: int = 500,
    temperature: float = 0.7
)
```

Free models available:
- `google/gemini-flash-1.5-8b` (Fast, good quality)
- `mistralai/mistral-7b-instruct` (Decent quality)
- `openchat/openchat-7b` (Basic quality)

## 🧪 Quick Test After Update

After getting a new key and updating `.env`:

```powershell
# 1. Test the API key directly
python test_openrouter_no_deps.py

# 2. Restart backend
cd backend
uv run uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000

# 3. Test in the app
# Open http://localhost:3000
# Upload PDF and send a message
```

## 📋 Checklist

- [ ] Go to https://openrouter.ai/keys
- [ ] Sign in / Sign up
- [ ] Generate new API key
- [ ] Copy the key
- [ ] Update `backend/.env` with new key
- [ ] Add credits to OpenRouter account (if using paid models)
- [ ] Restart backend server
- [ ] Test with `python test_openrouter_no_deps.py`
- [ ] Should see "✅ SUCCESS!"
- [ ] Test in web app at http://localhost:3000

## 🎯 Summary

**Issue**: API key is invalid (401 error)
**Cause**: Key expired, revoked, or never valid
**Solution**: Get new key from https://openrouter.ai/keys
**Status**: Needs action from you

Once you have a new valid API key, the chat will work with real AI responses! 🚀

## 🆘 Alternative: Use Free Mode

If you want to test without getting an OpenRouter key, you can comment out the API key:

`backend/.env`:
```env
# OPENROUTER_API_KEY=your-key-here
```

The app will work in **mock mode** with development responses. Not as smart, but good for testing the UI.
