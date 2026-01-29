# 🚀 Quick Start Guide - Demo Mode (No Twilio/AWS Required)

This guide will get your voice bot running in **5 minutes** for your interview demo!

---

## ✅ What You Need

1. **Python 3.11+** installed
2. **OpenAI API Key** (with Realtime API access)
3. **A microphone** (laptop mic is fine)
4. **Chrome/Edge browser** (for best audio support)

That's it! No Twilio, no AWS, no cloud deployment needed.

---

## 📦 Installation (2 minutes)

### Step 1: Setup Environment

```bash
# Navigate to project directory
cd quickrupee-voicebot

# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Add your OpenAI API key:**

```env
OPENAI_API_KEY=sk-proj-your-key-here
```

Save and close the file.

---

## 🎯 Run the Demo (1 minute)

```bash
# Start the demo server
python demo_server.py
```

You should see:

```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
🎙️  Demo Mode - No Twilio Required
📱 Open http://localhost:8000 in your browser
```

---

## 🎤 Test the Voice Bot

1. **Open your browser** and go to `http://localhost:8000`

2. **Click "Start Conversation"**

3. **Allow microphone access** when prompted

4. **Speak clearly:**
   - Wait for the greeting
   - Answer "Yes" or "No" to each question
   - The bot will ask 3 questions:
     - Are you a salaried employee?
     - Is your salary above ₹25,000?
     - Do you live in Delhi, Mumbai, or Bangalore?

5. **See the result:**
   - ✅ **Eligible**: "Agent will call back in 10 minutes"
   - ❌ **Not Eligible**: Polite rejection message

---

## 🎬 Interview Demo Script

### Test Scenario 1: Eligible Candidate

**Run through this for the interviewer:**

1. Start conversation
2. Answer: "Yes" (salaried)
3. Answer: "Yes" (salary ₹25K+)
4. Answer: "Yes" (metro city)
5. **Result**: ✅ Eligible

**Time**: ~60 seconds

---

### Test Scenario 2: Not Eligible (Salary)

1. Start conversation
2. Answer: "Yes" (salaried)
3. Answer: "No" (salary below ₹25K)
4. **Result**: ❌ Not eligible - Call ends early

**Time**: ~30 seconds

---

## 🏗️ Architecture Explanation (For Interview)

When presenting, explain:

```
┌──────────────┐
│   Browser    │ ← Your laptop microphone
│  (Frontend)  │
└──────┬───────┘
       │ WebSocket (Audio Stream)
       ↓
┌──────────────────┐
│  FastAPI Server  │ ← demo_server.py
│  Port 8000       │
└──────┬───────────┘
       │
       ↓
┌──────────────────────┐
│ OpenAI Realtime API  │ ← Speech-to-Text + Text-to-Speech
│ (Streaming STT/TTS)  │
└──────┬───────────────┘
       │
       ↓
┌──────────────────┐
│  State Machine   │ ← Rule-based eligibility logic
│  (Business Logic)│
└──────────────────┘
```

**Key Points:**
- "I used OpenAI's Realtime API for ultra-low latency STT/TTS"
- "The eligibility logic is rule-based, not LLM-based, for speed and determinism"
- "State machine ensures correct conversation flow"
- "For production, this would connect to Twilio for phone calls"

---

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "OpenAI API error"
- Check your API key in `.env`
- Verify you have Realtime API access (may need to request beta access)
- Check your OpenAI account has credits

### Issue: "Microphone not working"
- Make sure you clicked "Allow" for microphone access
- Try Chrome or Edge browser (best compatibility)
- Check your system microphone permissions

### Issue: "Bot doesn't understand me"
- Speak clearly and wait for the question to finish
- Use simple "Yes" or "No" answers
- Reduce background noise

### Issue: "WebSocket connection failed"
- Make sure the server is running (`python demo_server.py`)
- Check firewall isn't blocking localhost:8000
- Try refreshing the browser

---

## 📊 What to Show Interviewers

### 1. **Live Demo** (2-3 minutes)
- Run through one eligible scenario
- Run through one rejection scenario
- Show the real-time transcription
- Highlight the low latency

### 2. **Code Walkthrough** (5 minutes)
- **`state_machine.py`**: Show the finite state machine logic
- **`openai_realtime.py`**: Explain the streaming integration
- **`demo_server.py`**: WebSocket handling and orchestration
- **`static/demo.html`**: Browser interface (optional)

### 3. **Architecture Discussion** (3 minutes)
- Explain why you chose rule-based over LLM for eligibility
- Discuss latency optimizations
- How this scales to production with Twilio

### 4. **Testing** (2 minutes)
- Run the state machine tests: `python test_state_machine.py`
- Show different yes/no variations work

---

## 🎓 Interview Talking Points

### Why This Architecture?

**Interviewer**: "Why did you use a state machine instead of letting the LLM handle the conversation?"

**You**: "I separated concerns - OpenAI Realtime handles the speech processing for low latency, but the eligibility logic is rule-based. This gives us:
- **Speed**: No LLM calls for business logic
- **Determinism**: Same input always gives same output
- **Explainability**: We can audit every decision
- **Cost**: Cheaper than multiple LLM calls
- **Compliance**: Clear rules for regulatory requirements"

---

### Latency Optimization

**Interviewer**: "How did you handle latency?"

**You**: "Three key optimizations:
1. **OpenAI Realtime API**: Token-level streaming vs waiting for complete responses
2. **Buffered audio**: ~200ms chunks balance latency vs accuracy
3. **Async/await**: Non-blocking I/O for concurrent connections"

---

### Production Readiness

**Interviewer**: "Is this production-ready?"

**You**: "For demo purposes, yes. For production I'd add:
- **Twilio integration**: Real phone call handling
- **Database**: Log all conversations for analytics
- **Monitoring**: Sentry for errors, metrics for call quality
- **Security**: API rate limiting, Twilio signature validation
- **Scaling**: Redis for session management, load balancer
- **Testing**: Integration tests with mock audio"

---

## 📁 Project Structure

```
quickrupee-voicebot/
├── demo_server.py          ← Run this for demo!
├── static/
│   └── demo.html          ← Browser interface
├── state_machine.py       ← Eligibility logic (IMPORTANT)
├── openai_realtime.py     ← STT/TTS integration
├── config.py              ← Configuration
├── requirements.txt       ← Dependencies
├── .env                   ← Your API key (create this)
├── test_state_machine.py  ← Unit tests
└── README.md              ← Full documentation
```

---

## 🚀 Advanced: Running Tests

Before your interview, run the tests to ensure everything works:

```bash
# Test the state machine logic
python test_state_machine.py

# You should see:
# ✅ Eligible Candidate (All Yes)
# ✅ Not Salaried Employee
# ✅ Salary Below Threshold
# ✅ Not in Metro City
# ... etc
```

---

## 💡 Pro Tips

1. **Practice the demo** 2-3 times before the interview
2. **Have both scenarios ready**: eligible and not eligible
3. **Close other apps** to reduce background noise
4. **Use headphones** for clearer audio
5. **Have the architecture diagram ready** to show
6. **Be ready to walk through the code** - especially `state_machine.py`

---

## 🎯 Interview Checklist

Before the interview:

- [ ] Tested the demo at least once
- [ ] Verified microphone works in browser
- [ ] OpenAI API key is valid and has credits
- [ ] Ran `python test_state_machine.py` successfully
- [ ] Reviewed `state_machine.py` code
- [ ] Can explain the architecture diagram
- [ ] Prepared talking points about latency and scalability
- [ ] Have backup plan (show code if demo fails)

---

## 🆘 Emergency Backup Plan

**If the live demo fails during interview:**

1. **Show the tests instead:**
   ```bash
   python test_state_machine.py
   ```

2. **Walk through the code:**
   - Open `state_machine.py` and explain the logic
   - Show the conversation scripts
   - Demonstrate how state transitions work

3. **Show the architecture:**
   - Draw/show the diagram
   - Explain each component's role

4. **Explain what went wrong:**
   - Be honest: "OpenAI API might be having issues"
   - Show you understand the architecture anyway

---

## ✨ Next Steps After Interview

If they ask about enhancements:

1. **Multi-language support** - Hindi, Tamil for Indian users
2. **Analytics dashboard** - Call volumes, success rates
3. **CRM integration** - Auto-create leads in Salesforce
4. **Sentiment analysis** - Detect frustrated callers
5. **A/B testing** - Different conversation scripts

---

**Good luck with your interview! 🎉**

You've got this! The demo is simple but shows strong engineering judgment:
- Clean architecture
- Appropriate technology choices
- Production-minded thinking
- Latency-aware design

---

## 📞 Need Help?

Common issues and solutions:
- **Port 8000 busy**: Change `PORT=8001` in `.env`
- **Can't install packages**: Update pip: `pip install --upgrade pip`
- **OpenAI quota exceeded**: Check billing in OpenAI dashboard

**Remember**: Even if the demo has technical issues, being able to explain your architecture and decisions is what matters most!
