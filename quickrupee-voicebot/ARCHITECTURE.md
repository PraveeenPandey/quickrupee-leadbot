# QuickRupee Voice Bot - Architecture Document

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                         │
│                                                              │
│  Phone Call (Production)    OR    Browser (Demo)            │
└────────────────┬──────────────────────┬──────────────────────┘
                 │                      │
                 │                      │
┌────────────────▼────────┐  ┌─────────▼───────────────┐
│   Twilio/Exotel         │  │   Browser WebSocket     │
│   (Production)          │  │   (Demo/Testing)        │
│   - Phone numbers       │  │   - Microphone access   │
│   - Call routing        │  │   - Audio playback      │
│   - WebSocket stream    │  │   - Visual feedback     │
└────────────────┬────────┘  └─────────┬───────────────┘
                 │                      │
                 └──────────┬───────────┘
                            │
                            │ Audio Stream (WebSocket)
                            │
              ┌─────────────▼─────────────┐
              │    FASTAPI SERVER         │
              │  (Voice Gateway/Router)   │
              │                           │
              │  - WebSocket Handler      │
              │  - Session Management     │
              │  - Audio Routing          │
              │  - Orchestration          │
              └─────────────┬─────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            │               │               │
┌───────────▼──────┐ ┌──────▼──────┐ ┌─────▼─────────┐
│  OpenAI          │ │   State     │ │   Business    │
│  Realtime API    │ │   Machine   │ │   Logic       │
│                  │ │             │ │               │
│ - Speech-to-Text │ │ - Flow      │ │ - Eligibility │
│ - Text-to-Speech │ │   Control   │ │   Rules       │
│ - Streaming      │ │ - State     │ │ - Validation  │
│                  │ │   Tracking  │ │ - Decisions   │
└──────────────────┘ └─────────────┘ └───────────────┘
```

---

## 🔧 Component Details

### 1. Frontend Layer

#### Demo Mode (Browser)
- **Technology**: HTML5 + JavaScript
- **Audio**: Web Audio API, MediaRecorder
- **Communication**: WebSocket to backend
- **Features**:
  - Real-time microphone capture
  - Audio playback
  - Conversation transcript display
  - Visual status indicators

#### Production Mode (Telephony)
- **Technology**: Twilio/Exotel
- **Audio Format**: μ-law (8kHz) or PCM (24kHz)
- **Communication**: TwiML + WebSocket
- **Features**:
  - Inbound call handling
  - Audio streaming
  - Call control (hangup, hold)

---

### 2. Backend Layer (FastAPI)

#### Responsibilities
1. **WebSocket Management**
   - Accept connections from frontend/Twilio
   - Maintain session state
   - Route audio bidirectionally

2. **Orchestration**
   - Connect OpenAI Realtime API
   - Manage state machine transitions
   - Apply business rules

3. **Session Management**
   - Track active conversations
   - Store eligibility results
   - Handle cleanup

#### Key Files
- `demo_server.py` - Demo mode server (no Twilio)
- `main.py` - Production server (with Twilio)
- `config.py` - Configuration management

---

### 3. AI Layer (OpenAI Realtime API)

#### Speech-to-Text (STT)
- **Model**: Whisper (via Realtime API)
- **Latency**: ~300-500ms
- **Features**:
  - Token-level streaming
  - Server-side Voice Activity Detection (VAD)
  - Automatic punctuation

#### Text-to-Speech (TTS)
- **Voice**: Configurable (alloy, echo, nova, etc.)
- **Latency**: ~200-400ms
- **Features**:
  - Natural prosody
  - Streaming audio output
  - Multiple voice options

#### Why Realtime API?
- **Low Latency**: Token-level streaming vs batch processing
- **Bidirectional**: Simultaneous STT + TTS
- **Built-in VAD**: Automatic turn detection
- **Quality**: State-of-the-art models

---

### 4. Business Logic Layer (State Machine)

#### Design Pattern: Finite State Machine (FSM)

```
                    START
                      ↓
                  ┌───────┐
                  │GREETING│
                  └───┬───┘
                      │
                      ↓
              ┌──────────────┐
              │ASK_EMPLOYMENT│
              └───┬──────┬───┘
                  │      │
               YES│      │NO
                  │      │
                  ↓      ↓
          ┌──────────┐  │
          │ASK_SALARY│  │
          └───┬──┬───┘  │
              │  │      │
           YES│  │NO    │
              │  │      │
              ↓  ↓      ↓
         ┌────────┐  ┌──────────────┐
         │ASK_CITY│  │NOT_ELIGIBLE  │
         └───┬──┬─┘  │"Thank you..."│
             │  │    └──────────────┘
          YES│  │NO        ↓
             │  │        END
             ↓  ↓
        ┌────────┐
        │ELIGIBLE│
        │"Great! │
        │Agent..."
        └───┬────┘
            ↓
          END
```

#### Why State Machine Instead of LLM?

| Aspect | State Machine | LLM-Based |
|--------|---------------|-----------|
| **Speed** | ✅ Instant (<1ms) | ❌ Slow (1-3s) |
| **Cost** | ✅ Free | ❌ $0.01-0.03/call |
| **Deterministic** | ✅ Always same | ❌ Variable |
| **Explainable** | ✅ Clear rules | ❌ Black box |
| **Compliance** | ✅ Auditable | ❌ Hard to audit |
| **Hallucination** | ✅ Never | ❌ Possible |

**Interview Answer**: "I separated concerns - OpenAI handles speech processing where it excels, but business logic uses deterministic rules for reliability, auditability, and compliance."

#### Implementation
- **File**: `state_machine.py`
- **States**: Enum-based
- **Transitions**: Pure functions
- **Input Parsing**: Regex-based yes/no detection

---

## 📊 Data Flow

### Inbound Call Flow (Production)

```
1. User calls Twilio number
   ↓
2. Twilio webhook → POST /voice/incoming
   ↓
3. Backend returns TwiML with WebSocket URL
   ↓
4. Twilio establishes WebSocket connection
   ↓
5. Backend connects to OpenAI Realtime API
   ↓
6. Audio flows bidirectionally:
   User → Twilio → Backend → OpenAI (STT)
   OpenAI (TTS) → Backend → Twilio → User
   ↓
7. Transcripts trigger state machine transitions
   ↓
8. State machine generates responses
   ↓
9. Responses converted to speech via OpenAI TTS
   ↓
10. Eligibility decision → End call
```

### Demo Flow (Browser)

```
1. User opens http://localhost:8000
   ↓
2. Clicks "Start Conversation"
   ↓
3. Browser requests microphone access
   ↓
4. WebSocket connection to /demo/voice/{session_id}
   ↓
5. Backend connects to OpenAI Realtime API
   ↓
6. Audio flows:
   Browser Mic → WebSocket → OpenAI (STT)
   OpenAI (TTS) → WebSocket → Browser Speakers
   ↓
7. Transcripts displayed in UI
   ↓
8. State machine processes responses
   ↓
9. Eligibility result shown in UI
```

---

## 🔄 State Machine Details

### States

```python
class State(Enum):
    INIT = "init"                # Initial state
    GREETING = "greeting"        # Playing welcome message
    ASK_EMPLOYMENT = "ask_employment"  # Question 1
    ASK_SALARY = "ask_salary"    # Question 2
    ASK_CITY = "ask_city"        # Question 3
    ELIGIBLE = "eligible"        # Success outcome
    NOT_ELIGIBLE = "not_eligible" # Rejection outcome
    END = "end"                  # Conversation complete
```

### Eligibility Rules

```python
# Rule 1: Must be salaried
if not is_salaried:
    return NOT_ELIGIBLE

# Rule 2: Salary must be ≥ ₹25,000
if salary < 25000:
    return NOT_ELIGIBLE

# Rule 3: Must live in metro city
if city not in ["Delhi", "Mumbai", "Bangalore"]:
    return NOT_ELIGIBLE

# All checks passed
return ELIGIBLE
```

### Yes/No Detection

```python
# Affirmative patterns
yes_patterns = [
    r'\byes\b', r'\byeah\b', r'\byep\b',
    r'\bsure\b', r'\bha\b', r'\bhaan\b'  # Hindi
]

# Negative patterns
no_patterns = [
    r'\bno\b', r'\bnope\b', r'\bnah\b',
    r'\bnot\b', r'\bnahi\b'  # Hindi
]

# Default to False for safety
```

---

## ⚡ Performance Optimizations

### 1. Audio Buffering
- **Chunk Size**: 4096 samples (~170ms at 24kHz)
- **Buffer**: 10 chunks (~1.7s) before sending
- **Trade-off**: Latency vs accuracy

### 2. Streaming
- **OpenAI**: Token-level streaming
- **WebSocket**: Binary frames for audio
- **No Blocking**: Async/await throughout

### 3. Voice Activity Detection
- **Server-side VAD**: OpenAI detects speech end
- **Threshold**: 0.5 (configurable)
- **Silence Duration**: 500ms

### 4. Connection Pooling
- **OpenAI WebSocket**: Persistent connection
- **Reuse**: Same connection for full conversation
- **Cleanup**: Graceful close on end

---

## 🔒 Security Considerations

### Current (Demo)
- Environment variables for secrets
- HTTPS/WSS in production
- Input validation

### Production Additions Needed
1. **Twilio Signature Validation**
   ```python
   from twilio.request_validator import RequestValidator
   # Verify requests actually from Twilio
   ```

2. **Rate Limiting**
   ```python
   from slowapi import Limiter
   # Prevent abuse
   ```

3. **Authentication**
   - API key rotation
   - IP whitelisting
   - Request signing

4. **Data Privacy**
   - PII encryption
   - Call recording consent
   - GDPR compliance

---

## 📈 Scalability

### Vertical Scaling
- **Current**: Single server
- **Scale to**: 4 vCPU, 8GB RAM
- **Handles**: ~100 concurrent calls

### Horizontal Scaling
```
┌─────────────┐
│Load Balancer│
│   (Nginx)   │
└──────┬──────┘
       │
   ┌───┴───────┬─────────┐
   │           │         │
┌──▼──┐    ┌──▼──┐  ┌──▼──┐
│App 1│    │App 2│  │App 3│
└─────┘    └─────┘  └─────┘
   │           │         │
   └───────┬───┴─────────┘
           │
    ┌──────▼──────┐
    │Redis Session│
    │   Storage   │
    └─────────────┘
```

### Database (Future)
- **PostgreSQL**: Call records, eligibility results
- **Redis**: Session state, real-time analytics
- **S3**: Call recordings (if enabled)

---

## 🧪 Testing Strategy

### Unit Tests
```python
# test_state_machine.py
def test_eligible_flow():
    sm = EligibilityStateMachine()
    assert sm.process_response("yes")["state"] == "ask_salary"
    assert sm.process_response("yes")["state"] == "ask_city"
    assert sm.process_response("yes")["is_eligible"] == True
```

### Integration Tests
```python
# test_openai_integration.py
async def test_stt_flow():
    client = OpenAIRealtimeClient()
    await client.connect()
    # Send audio, verify transcript
```

### End-to-End Tests
- Selenium browser automation
- Mock OpenAI responses
- Twilio test credentials

---

## 📊 Monitoring & Analytics

### Metrics to Track
1. **Call Volume**
   - Total calls/day
   - Peak hours
   - Average duration

2. **Eligibility Rates**
   - % eligible
   - Rejection reasons breakdown
   - Conversion funnel

3. **Performance**
   - Average latency
   - OpenAI response time
   - WebSocket errors

4. **Quality**
   - Transcription accuracy
   - Failed calls
   - User disconnections

### Tools
- **Sentry**: Error tracking
- **Datadog**: APM and metrics
- **Mixpanel**: User analytics
- **Twilio Console**: Call logs

---

## 🚀 Deployment Options

### Demo (Current)
```bash
python demo_server.py
# Access at http://localhost:8000
```

### Production Options

1. **AWS EC2**
   - Ubuntu 22.04
   - Docker Compose
   - Nginx reverse proxy
   - Let's Encrypt SSL

2. **Fly.io**
   - `flyctl deploy`
   - Auto-scaling
   - Global edge network

3. **Railway/Render**
   - Git push deployment
   - Auto HTTPS
   - Built-in monitoring

---

## 💰 Cost Analysis

### Per 1000 Call Minutes

| Component | Cost | Notes |
|-----------|------|-------|
| OpenAI Realtime | $3-5 | Varies by usage |
| Twilio Voice | $13 | $0.013/min |
| Compute | $15-20 | AWS t3.small |
| **Total** | **$31-38** | ~$0.03-0.04/min |

### Optimization Ideas
- Cache common responses
- Use regional servers
- Negotiate Twilio volume discount

---

## 🎯 Future Enhancements

### Phase 2
- [ ] Multi-language (Hindi, Tamil)
- [ ] SMS notifications for eligible users
- [ ] CRM integration (Salesforce)
- [ ] Analytics dashboard

### Phase 3
- [ ] Sentiment analysis
- [ ] Dynamic eligibility rules
- [ ] A/B testing framework
- [ ] Voice biometrics

### Phase 4
- [ ] Video calling (Twilio Video)
- [ ] AI-powered negotiation
- [ ] Fraud detection
- [ ] Automated loan approval

---

## 📚 Key Technologies

| Layer | Technology | Why? |
|-------|-----------|------|
| Backend | FastAPI | High performance, async |
| STT/TTS | OpenAI Realtime | Low latency, high quality |
| Logic | State Machine | Fast, deterministic |
| Telephony | Twilio/Exotel | Reliable, feature-rich |
| Deployment | Docker | Portable, reproducible |
| Language | Python 3.11 | Type hints, async support |

---

## 🎓 Interview Discussion Points

### Architecture Decisions
1. **Why FastAPI?** - Async support, performance, type safety
2. **Why State Machine?** - Speed, determinism, compliance
3. **Why OpenAI Realtime?** - Best-in-class latency and quality
4. **Why Separate STT/TTS from Logic?** - Separation of concerns

### Trade-offs
1. **Latency vs Accuracy** - Smaller audio buffers = faster but less accurate
2. **Cost vs Quality** - Premium voices cost more but convert better
3. **Flexibility vs Speed** - Hard-coded rules are fast but inflexible

### Scalability
1. **Current bottleneck**: OpenAI API rate limits
2. **Solution**: Request limit increase, caching
3. **Next bottleneck**: Single server
4. **Solution**: Load balancer + multiple instances

---

This architecture is designed to be:
- ✅ **Interview-friendly**: Easy to explain and defend
- ✅ **Production-ready**: With clear upgrade path
- ✅ **Cost-effective**: Minimal infrastructure
- ✅ **Maintainable**: Clean separation of concerns
