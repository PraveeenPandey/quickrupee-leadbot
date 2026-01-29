# QuickRupee Voice Bot 🎙️

An AI-powered voice bot that screens loan applicants through automated conversations. Built for interview demonstration - runs entirely on your laptop with just an OpenAI API key.

---

## Quick Start (3 Steps)

### 1. Install Dependencies

```bash
cd quickrupee-voicebot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-proj-your-key-here
```

### 3. Run the Demo

```bash
python demo_server.py
```

Open `http://localhost:8000` in Chrome or Edge browser.

---

## What It Does

Screens loan applicants with 3 questions:

1. **"Are you a salaried employee?"**
2. **"Is your monthly salary above ₹25,000?"**
3. **"Do you live in Delhi, Mumbai, or Bangalore?"**

**All Yes** → Eligible (agent will call back)
**Any No** → Not eligible (call ends)

---

## Architecture

```
Browser Microphone
    ↓ WebSocket
FastAPI Server (Python)
    ↓
OpenAI Realtime API
   (STT + TTS)
    ↓
State Machine
  (Eligibility Rules)
```

**Key Decision:** Rule-based state machine for eligibility checks (not LLM) because:
- **Faster** - Instant vs 1-3 seconds
- **Deterministic** - No AI hallucinations
- **Auditable** - Regulatory compliance
- **Cheaper** - No extra API calls

---

## Project Structure

```
quickrupee-voicebot/
├── demo_server.py          ← Run this!
├── state_machine.py        ← Eligibility logic
├── openai_realtime.py      ← STT/TTS integration
├── config.py               ← Configuration
├── static/demo.html        ← Browser interface
├── test_state_machine.py   ← Unit tests
└── requirements.txt        ← Dependencies
```

---

## Testing

```bash
# Test business logic
python test_state_machine.py

# Test demo scenarios
# 1. Open http://localhost:8000
# 2. Click "Start Conversation"
# 3. Answer "Yes" to all → Should be eligible
# 4. Try "Yes", "No" → Should reject early
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | High-performance async web framework |
| STT/TTS | OpenAI Realtime API | Ultra-low latency speech processing |
| Logic | Python State Machine | Deterministic eligibility rules |
| Frontend | HTML5 + Web Audio API | Browser-based demo interface |
| Audio | WebSocket | Bidirectional streaming |

---

## Features

**Ultra-low latency** - OpenAI Realtime API with token-level streaming
**Rule-based logic** - Fast, explainable eligibility decisions
**State machine** - Deterministic conversation flow
**Browser-based** - No phone number or cloud setup needed
**Production-ready patterns** - Easy to add telephony later

---

## Interview Talking Points

### Why State Machine Instead of LLM?

"I separated concerns - OpenAI handles speech processing where it excels, but business logic uses deterministic rules because:
- **Speed**: Sub-millisecond decisions
- **Reliability**: No hallucinations on eligibility
- **Compliance**: Every decision is auditable
- **Cost**: No additional API calls"

### How to Deploy to Production?

"The architecture is production-ready. To deploy with real phone calls:
- Add Twilio for telephony (replace browser WebSocket)
- Deploy to AWS EC2 or Fly.io
- Add Nginx reverse proxy with SSL
- Store results in PostgreSQL
- Add Redis for session management
- The core logic stays the same"

### Latency Optimization?

"Three key optimizations:
1. OpenAI Realtime API - token-level streaming
2. Audio buffering - ~200ms chunks
3. Async/await - non-blocking I/O throughout"

---

## 📖 Documentation

- **START_HERE.md** - Quick overview
- **DEMO_QUICKSTART.md** - Detailed setup guide
- **ARCHITECTURE.md** - Technical deep dive

---

## Troubleshooting

**Module not found**
```bash
pip install -r requirements.txt
```

**OpenAI API error**
- Check `.env` has valid API key
- Verify OpenAI account has credits
- Confirm you have Realtime API access

**Microphone not working**
- Click "Allow" for microphone access
- Use Chrome or Edge browser
- Check system microphone permissions

**Bot doesn't understand**
- Speak clearly with "Yes" or "No"
- Reduce background noise
- Wait for question to finish

---

## Next Steps

### For Production Deployment:
- Integrate Twilio for phone calls
- Add database for call logging
- Implement monitoring (Sentry, Datadog)
- Add rate limiting and security

### For Enhanced Features:
- Multi-language support (Hindi, Tamil)
- CRM integration (Salesforce)
- Analytics dashboard
- Sentiment analysis

---

## Cost Estimate (Production Scale)

For 1,000 minutes of calls:
- OpenAI Realtime API: ~$3-5
- Twilio Voice: ~$13
- Cloud hosting: ~$15
- **Total: ~$31-33/month**

---

## Pre-Interview Checklist

- [ ] Run `python demo_server.py` successfully
- [ ] Test eligible flow (all "Yes")
- [ ] Test rejection flow (any "No")
- [ ] Run `python test_state_machine.py`
- [ ] Review `state_machine.py` code
- [ ] Can explain architecture diagram
- [ ] Prepared talking points

---

## License

MIT License - Free to use for interview projects and learning

---

**Built for QuickRupee Interview Assignment**

Demonstrates:
- Real-time AI speech processing
- Smart architecture decisions
- Production-ready code patterns
- Strong engineering judgment

**Run `python demo_server.py` and open http://localhost:8000 to start!**
