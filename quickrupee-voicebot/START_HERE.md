# 👋 START HERE - QuickRupee Voice Bot

## What Is This?

An AI-powered voice bot that screens loan applicants through automated conversations. Built for **QuickRupee interview assignment** - runs entirely on your laptop, no cloud setup needed!

---

## ⚡ Get Running in 5 Minutes

```bash
# 1. Install dependencies (2 min)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Add OpenAI API key (1 min)
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-proj-your-key-here

# 3. Run the demo (1 min)
python demo_server.py

# 4. Test it (2 min)
# Open http://localhost:8000 in Chrome/Edge
# Click "Start Conversation"
# Allow microphone access
# Answer the 3 questions with "Yes" or "No"
```

---

## 🎯 What It Does

The bot asks 3 questions to screen loan applicants:

1. **"Are you a salaried employee?"** → Yes/No
2. **"Is your salary above ₹25,000?"** → Yes/No
3. **"Do you live in Delhi, Mumbai, or Bangalore?"** → Yes/No

**Result:**
- All Yes = ✅ **Eligible** "Agent will call back in 10 minutes"
- Any No = ❌ **Not Eligible** "You don't meet our criteria"

---

## 📁 Key Files

```
quickrupee-voicebot/
├── demo_server.py          ← Run this to start!
├── state_machine.py        ← Eligibility logic (most important!)
├── openai_realtime.py      ← STT/TTS integration
├── config.py               ← Settings
├── static/demo.html        ← Browser UI
└── test_state_machine.py   ← Unit tests
```

**Focus on `state_machine.py` for interview - it's the heart of the logic.**

---

## 🏗️ Architecture (Simple)

```
Your Microphone
     ↓
  Browser
     ↓ WebSocket
FastAPI Server
     ↓
OpenAI Realtime
  (STT + TTS)
     ↓
State Machine
  (Rules)
```

**Key Insight:** Uses **rule-based state machine** (not LLM) for eligibility because:
- ⚡ Faster (instant vs 1-3 seconds)
- 🎯 Deterministic (no hallucinations)
- 📋 Auditable (compliance)
- 💰 Cheaper (no extra API calls)

---

## ✅ Pre-Interview Checklist

- [ ] Run `python demo_server.py`
- [ ] Test eligible flow (all "Yes")
- [ ] Test rejection flow (any "No")
- [ ] Run `python test_state_machine.py`
- [ ] Read `state_machine.py` code
- [ ] Can explain: "Why state machine vs LLM?"

---

## 🎤 Quick Demo (60 seconds)

**Test 1: Eligible User**
- Say "Yes" → "Yes" → "Yes"
- Result: ✅ Eligible

**Test 2: Rejected User**
- Say "Yes" → "No"
- Result: ❌ Call ends early

**This shows:**
- Real-time speech recognition
- Smart conversation flow
- Early termination on rejection

---

## 💡 Top Interview Questions

### Q: "Why state machine instead of LLM?"

**A:** "OpenAI handles speech processing, but I used rules for eligibility because:
- Speed: Instant decisions
- Reliability: No hallucinations
- Compliance: Auditable decisions
- Cost: No extra API calls"

### Q: "How to deploy to production?"

**A:** "Add Twilio for phone calls, deploy to AWS/Fly.io, add database and monitoring. The core logic stays the same."

### Q: "How did you optimize latency?"

**A:** "OpenAI Realtime API with streaming, ~200ms audio buffering, async/await architecture."

---

## 🐛 Quick Fixes

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"OpenAI error"**
- Check `.env` has: `OPENAI_API_KEY=sk-proj-...`
- Verify OpenAI account has credits

**"Microphone not working"**
- Click "Allow" for mic access
- Use Chrome or Edge
- Check system mic permissions

---

## 📚 Read Next

1. **README.md** - Full project overview
2. **DEMO_QUICKSTART.md** - Detailed setup guide
3. **ARCHITECTURE.md** - Technical deep dive

---

## 🎯 You're Ready When You Can:

✅ Run both demo scenarios (eligible & not eligible)
✅ Explain state machine vs LLM decision
✅ Walk through `state_machine.py` code
✅ Describe production deployment path
✅ Discuss latency optimizations

---

## 🚀 Now Run It!

```bash
python demo_server.py
# Open http://localhost:8000
```

**Good luck with your interview!** 💪

You've built a production-quality voice bot that shows:
- Clean architecture
- Smart technical decisions
- Real-time AI integration
- Production-ready patterns

**Go crush it!** 🎉
