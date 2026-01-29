# How to Interact with QuickRupee Voice Bot

## 🎤 Method 1: Browser Voice Demo (Recommended)

This is the main way to interact - speak to the bot using your microphone.

### Step 1: Start the Server

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run the server
python demo_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
🎙️  Demo Mode - No Twilio Required
📱 Open http://localhost:8000 in your browser
```

### Step 2: Open Browser

1. Open **Chrome** or **Edge** browser (best compatibility)
2. Navigate to: `http://localhost:8000`
3. You'll see the QuickRupee Voice Bot interface

### Step 3: Start Conversation

1. Click the green **"Start Conversation"** button
2. Browser will ask for microphone permission - **Click "Allow"**
3. Wait ~2 seconds for connection
4. You'll see "Connected" status turn green
5. The bot will greet you:
   > "Hello! Welcome to QuickRupee Personal Loans. I'll ask you three quick questions..."

### Step 4: Interact with Voice

**The bot will ask 3 questions. Speak clearly after each question:**

#### Question 1: Employment
- **Bot asks:** "Are you currently a salaried employee? Please say Yes or No."
- **You say:** "Yes" or "No" (speak clearly)
- **You'll see:** Your answer transcribed on screen

#### Question 2: Salary (if you said Yes to Q1)
- **Bot asks:** "Is your monthly in-hand salary above 25,000 rupees? Please say Yes or No."
- **You say:** "Yes" or "No"
- **You'll see:** Your answer transcribed on screen

#### Question 3: City (if you said Yes to Q2)
- **Bot asks:** "Do you currently live in a metro city such as Delhi, Mumbai, or Bangalore? Please say Yes or No."
- **You say:** "Yes" or "No"
- **You'll see:** Your answer transcribed on screen

### Step 5: See Result

**If you answered Yes to all 3 questions:**
```
✅ ELIGIBLE
An agent will call you back within 10 minutes
```

**If you answered No to any question:**
```
❌ NOT ELIGIBLE
You do not meet the current criteria
```

The call ends automatically after showing the result.

---

## 🎯 Sample Conversations

### Conversation 1: Eligible User (60 seconds)

```
Bot: "Hello! Welcome to QuickRupee Personal Loans..."

Bot: "Are you currently a salaried employee?"
You: "Yes"

Bot: "Is your monthly in-hand salary above 25,000 rupees?"
You: "Yes"

Bot: "Do you currently live in a metro city..."
You: "Yes"

Bot: "Great news! You are eligible for a QuickRupee personal loan..."
Result: ✅ ELIGIBLE
```

### Conversation 2: Not Eligible - Salary (30 seconds)

```
Bot: "Hello! Welcome to QuickRupee Personal Loans..."

Bot: "Are you currently a salaried employee?"
You: "Yes"

Bot: "Is your monthly in-hand salary above 25,000 rupees?"
You: "No"

Bot: "Thank you for your interest in QuickRupee. At the moment..."
Result: ❌ NOT ELIGIBLE
(Call ends early - doesn't ask Question 3)
```

### Conversation 3: Not Eligible - Not Salaried (15 seconds)

```
Bot: "Hello! Welcome to QuickRupee Personal Loans..."

Bot: "Are you currently a salaried employee?"
You: "No"

Bot: "Thank you for your interest in QuickRupee..."
Result: ❌ NOT ELIGIBLE
(Call ends immediately - skips Questions 2 and 3)
```

---

## 🧪 Method 2: Test Without Voice (For Testing Logic)

You can test the business logic directly without using your microphone.

### Run the Unit Tests

```bash
python test_state_machine.py
```

**Output:**
```
🧪 QuickRupee Voice Bot - State Machine Tests
============================================================
Testing Scenario: Eligible Candidate (All Yes)
============================================================
Bot: Hello! Welcome to QuickRupee Personal Loans...

User: yes
Bot: Are you currently a salaried employee? Please say Yes or No.
State: ask_employment

User: yes
Bot: Is your monthly in-hand salary above 25000 rupees?
State: ask_salary

User: yes
Bot: Do you currently live in a metro city...
State: ask_city

User: yes
Bot: Great news! You are eligible...
State: eligible

✓ Call ended
✓ Eligible: True

============================================================
Testing Scenario: Not Salaried Employee
============================================================
...

✅ All tests completed!
```

---

## 💡 Tips for Best Experience

### Voice Recognition Tips

✅ **DO:**
- Speak clearly and at normal pace
- Say simple "Yes" or "No"
- Wait for question to finish before answering
- Use a quiet environment
- Speak directly toward your microphone

❌ **DON'T:**
- Mumble or speak too fast
- Use long sentences ("Yes, I am" - just say "Yes")
- Interrupt the bot while it's speaking
- Have loud background noise
- Cover your microphone

### Accepted Responses

The bot understands various ways to say yes/no:

**Affirmative:**
- "Yes"
- "Yeah"
- "Yep"
- "Sure"
- "Correct"
- "Ha" / "Haan" (Hindi)

**Negative:**
- "No"
- "Nope"
- "Nah"
- "Not"
- "Nahi" / "Nahin" (Hindi)

---

## 🎬 Visual Guide

### 1. Initial Screen
```
┌─────────────────────────────────────┐
│   🎙️ QuickRupee Voice Bot          │
│                                      │
│   [🎤 Start Conversation]           │
│                                      │
└─────────────────────────────────────┘
```

### 2. During Conversation
```
┌─────────────────────────────────────┐
│   Status: 🟢 Connected              │
│   State: ask_employment              │
├─────────────────────────────────────┤
│   Bot: Are you currently a          │
│        salaried employee?           │
│                                      │
│   User: Yes                          │
│                                      │
│   🔴 Listening...                   │
├─────────────────────────────────────┤
│   [⏹️ End Call]                     │
└─────────────────────────────────────┘
```

### 3. Final Result
```
┌─────────────────────────────────────┐
│   ✅ ELIGIBLE                       │
│   An agent will call you back       │
│   within 10 minutes                 │
│                                      │
│   [🎤 Start New Conversation]      │
└─────────────────────────────────────┘
```

---

## 🐛 Troubleshooting Interactions

### Problem: Bot doesn't hear me

**Solutions:**
1. Check microphone is working (try recording in another app)
2. Make sure you clicked "Allow" for microphone access
3. Refresh the page and try again
4. Check browser console for errors (F12)

### Problem: Bot misunderstands my answer

**Solutions:**
1. Speak more clearly
2. Use simple "Yes" or "No" only
3. Reduce background noise
4. Move closer to microphone
5. Try again with clearer pronunciation

### Problem: Bot response is slow

**Possible causes:**
1. Slow internet connection
2. OpenAI API latency (check status.openai.com)
3. Computer CPU overloaded

### Problem: Can't connect to server

**Solutions:**
1. Make sure server is running (`python demo_server.py`)
2. Check you're accessing correct URL: `http://localhost:8000`
3. Try different port: Edit `.env` → `PORT=8001`, restart server
4. Check firewall isn't blocking localhost

---

## 🎯 Interview Demo Flow

For presenting to interviewers:

### Demo Script (2 minutes)

**Opening:**
"Let me demonstrate the QuickRupee voice bot. I'll show both an eligible and non-eligible scenario."

**Scenario 1: Eligible (60 sec)**
1. "I'm starting the conversation..."
2. Click "Start Conversation"
3. "The bot is asking about employment..." → Say "Yes"
4. "Now asking about salary..." → Say "Yes"
5. "Finally asking about location..." → Say "Yes"
6. "As you can see, the user is marked as eligible"

**Scenario 2: Not Eligible (30 sec)**
1. "Let me show what happens if criteria aren't met..."
2. Click "Start Conversation"
3. "Same first question..." → Say "Yes"
4. "But now I'll say the salary is too low..." → Say "No"
5. "Notice the bot ends the call early - it doesn't waste time asking the third question"

**Closing:**
"This demonstrates the smart state machine that efficiently screens applicants and only continues if they're potentially eligible."

---

## 📊 What Happens Behind the Scenes

When you interact with the bot:

1. **Your speech** → Captured by browser microphone
2. **Audio data** → Sent via WebSocket to FastAPI server
3. **Server** → Forwards audio to OpenAI Realtime API
4. **OpenAI** → Transcribes speech to text (STT)
5. **Server** → Receives transcript, sends to state machine
6. **State Machine** → Processes answer, determines next question
7. **Server** → Sends response text to OpenAI for TTS
8. **OpenAI** → Converts text to speech audio
9. **Server** → Streams audio back to browser
10. **Browser** → Plays audio through speakers

**Total round-trip: <1 second** ⚡

---

## 🔍 Monitoring Your Interaction

### Server Console Output

When you interact, you'll see logs like:

```
INFO: Demo session started: demo_1706534567890
INFO: User said: yes
INFO: State: ask_salary, Should end: False
INFO: User said: yes
INFO: State: ask_city, Should end: False
INFO: User said: yes
INFO: State: eligible, Should end: True
INFO: Cleaned up demo session: demo_1706534567890
```

### Browser Console (F12 → Console Tab)

```
WebSocket connected
Received: {"type": "ready", "message": "Connected to voice bot"}
Received: {"type": "bot_message", "text": "Hello! Welcome..."}
Received: {"type": "transcript", "text": "yes", "role": "user"}
Received: {"type": "state_update", "state": "ask_salary"}
```

---

## 🎓 Understanding the Interaction Flow

```
┌──────────────┐
│     USER     │
│   (speaks)   │
└──────┬───────┘
       │
       ↓ "Yes"
┌──────────────────┐
│    BROWSER       │
│  - Microphone    │
│  - Audio Capture │
└──────┬───────────┘
       │
       ↓ Audio bytes
┌──────────────────────┐
│  FASTAPI SERVER      │
│  - WebSocket Handler │
└──────┬───────────────┘
       │
       ↓ Audio stream
┌──────────────────────┐
│  OPENAI REALTIME     │
│  - Speech-to-Text    │
└──────┬───────────────┘
       │
       ↓ "yes" (text)
┌──────────────────────┐
│  STATE MACHINE       │
│  - Check rules       │
│  - Next question     │
└──────┬───────────────┘
       │
       ↓ "Is your salary..."
┌──────────────────────┐
│  OPENAI REALTIME     │
│  - Text-to-Speech    │
└──────┬───────────────┘
       │
       ↓ Audio bytes
┌──────────────────────┐
│    BROWSER           │
│  - Play audio        │
└──────┬───────────────┘
       │
       ↓ Sound waves
┌──────────────┐
│     USER     │
│   (hears)    │
└──────────────┘
```

---

## ✅ Quick Reference

### To Start:
```bash
python demo_server.py
# Open http://localhost:8000
```

### To Interact:
1. Click "Start Conversation"
2. Allow microphone
3. Answer "Yes" or "No" to each question
4. See your eligibility result

### To Test Logic:
```bash
python test_state_machine.py
```

### To Stop:
- Click "End Call" button, or
- Press `Ctrl+C` in terminal

---

**That's it! You're now ready to interact with your voice bot!** 🎉
