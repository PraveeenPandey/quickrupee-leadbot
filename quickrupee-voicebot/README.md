# QuickRupee Voice Bot

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

## Conversation Flow Diagram

```mermaid
flowchart TD
    A[User Calls] --> B[Greeting]
    B --> C{Are you a salaried employee?}

    C -->|Yes| D{Is salary above 25,000?}
    C -->|No| R1[Not Eligible - Not Salaried]
    C -->|Invalid| C1[Please say Yes or No]
    C1 --> C

    D -->|Yes| E{Live in Metro City?}
    D -->|No| R2[Not Eligible - Low Salary]
    D -->|Invalid| D1[Please say Yes or No]
    D1 --> D

    E -->|Yes| S[Eligible - Agent Callback]
    E -->|No| R3[Not Eligible - Not in Metro]
    E -->|Invalid| E1[Please say Yes or No]
    E1 --> E

    R1 --> END[Call Ends]
    R2 --> END
    R3 --> END
    S --> END

    style A fill:#e1f5fe
    style S fill:#c8e6c9
    style R1 fill:#ffcdd2
    style R2 fill:#ffcdd2
    style R3 fill:#ffcdd2
    style END fill:#f5f5f5
```

---

## State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> INIT
    INIT --> GREETING: start()
    GREETING --> ASK_EMPLOYMENT: process_response("")

    ASK_EMPLOYMENT --> ASK_SALARY: Yes
    ASK_EMPLOYMENT --> NOT_ELIGIBLE: No
    ASK_EMPLOYMENT --> ASK_EMPLOYMENT: Invalid Response

    ASK_SALARY --> ASK_CITY: Yes
    ASK_SALARY --> NOT_ELIGIBLE: No
    ASK_SALARY --> ASK_SALARY: Invalid Response

    ASK_CITY --> ELIGIBLE: Yes
    ASK_CITY --> NOT_ELIGIBLE: No
    ASK_CITY --> ASK_CITY: Invalid Response

    ELIGIBLE --> [*]
    NOT_ELIGIBLE --> [*]
```

---

## System Architecture

```mermaid
flowchart LR
    subgraph Browser
        MIC[Microphone] --> |PCM16 Audio| WS[WebSocket]
        SPK[Speaker] --> |MP3 Audio| WS
    end

    subgraph Server["FastAPI Server"]
        WS --> |Audio Stream| RT[OpenAI Realtime API]
        RT --> |Transcript| SM[State Machine]
        SM --> |Response Text| TTS[OpenAI TTS API]
        TTS --> |Cached MP3| WS
    end

    subgraph Cache["TTS Cache"]
        TTS -.-> |Pre-loaded| CACHE[(Audio Cache)]
        CACHE -.-> |Instant| WS
    end

    style MIC fill:#e3f2fd
    style SPK fill:#e8f5e9
    style SM fill:#fff3e0
    style CACHE fill:#f3e5f5
```

---

## What It Does

Screens loan applicants with 3 questions:

1. **"Are you a salaried employee?"**
2. **"Is your monthly salary above 25,000?"**
3. **"Do you live in Delhi, Mumbai, or Bangalore?"**

| Response | Result |
|----------|--------|
| All Yes | Eligible (agent will call back) |
| Any No | Not eligible (call ends politely) |
| Invalid | Re-asks with clarification |

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Hybrid Speech Processing** | Realtime API for STT, Standard TTS API for speech |
| **TTS Caching** | Pre-loads all responses at startup for instant playback |
| **Input Validation** | Re-asks if user doesn't say Yes/No |
| **Mic Muting** | Prevents bot from hearing itself |
| **Rule-based Logic** | Deterministic, auditable eligibility decisions |

---

## Project Structure

```
quickrupee-voicebot/
├── demo_server.py          <- Main server (run this!)
├── state_machine.py        <- Eligibility logic & scripts
├── openai_realtime.py      <- Speech-to-text integration
├── config.py               <- Configuration settings
├── static/demo.html        <- Browser interface
├── test_state_machine.py   <- Unit tests
└── requirements.txt        <- Dependencies
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | High-performance async web framework |
| STT | OpenAI Realtime API | Real-time speech transcription with VAD |
| TTS | OpenAI TTS API | Text-to-speech with caching |
| Logic | Python State Machine | Deterministic eligibility rules |
| Frontend | HTML5 + Web Audio API | Browser-based demo interface |
| Transport | WebSocket | Bidirectional streaming |

---

## Audio Flow

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant S as Server
    participant O as OpenAI

    Note over S: Startup: Pre-load TTS Cache
    S->>O: Generate audio for all scripts
    O-->>S: Cache 9 audio files

    U->>B: Click Start
    B->>S: WebSocket Connect
    S->>O: Connect Realtime API

    Note over S: Greeting (from cache)
    S-->>B: MP3 Audio (instant)
    B->>U: Play greeting

    Note over S: Question 1 (from cache)
    S-->>B: MP3 Audio (instant)
    B->>U: Play question

    U->>B: Says "Yes"
    B->>S: PCM16 Audio Stream
    S->>O: Audio for transcription
    O-->>S: Transcript: "Yes"

    Note over S: Question 2 (from cache)
    S-->>B: MP3 Audio (instant)
    B->>U: Play question
```

---

## Testing

```bash
# Test business logic
python test_state_machine.py

# Test demo scenarios
# 1. Open http://localhost:8000
# 2. Click "Start Conversation"
# 3. Answer "Yes" to all -> Should be eligible
# 4. Try "Yes", "No" -> Should reject early
```

---
