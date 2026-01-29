"""
QuickRupee Voice Bot - Simple Demo Server
Uses text input + OpenAI TTS for reliable demo
No complex bidirectional streaming - just works!
"""
import asyncio
import logging
import base64
import httpx
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from state_machine import EligibilityStateMachine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Active sessions
sessions: Dict[str, EligibilityStateMachine] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    logger.info("=" * 60)
    logger.info("🎙️  QuickRupee Voice Bot - Simple Demo")
    logger.info("📱 Open http://localhost:8000 in your browser")
    logger.info("=" * 60)
    yield
    sessions.clear()


app = FastAPI(
    title="QuickRupee Voice Bot - Simple Demo",
    description="Text input + TTS output for reliable demo",
    version="2.0.0",
    lifespan=lifespan,
)


async def text_to_speech(text: str) -> Optional[bytes]:
    """Convert text to speech using OpenAI TTS API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "tts-1",
                    "input": text,
                    "voice": settings.VOICE,
                    "response_format": "mp3",
                },
                timeout=30.0,
            )
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None


@app.get("/")
async def root():
    """Serve the simple demo interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuickRupee Voice Bot - Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 700px;
            width: 100%;
            padding: 40px;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { font-size: 48px; margin-bottom: 10px; }
        h1 { color: #333; font-size: 28px; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 14px; }
        .status-bar {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-indicator {
            width: 12px; height: 12px;
            border-radius: 50%;
            background: #dc3545;
            display: inline-block;
            margin-right: 8px;
        }
        .status-indicator.connected { background: #28a745; }
        .conversation-area {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            min-height: 300px;
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 10px;
            max-width: 85%;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.bot {
            background: #667eea;
            color: white;
            margin-right: auto;
        }
        .message.user {
            background: #28a745;
            color: white;
            margin-left: auto;
        }
        .message.system {
            background: #ffc107;
            color: #333;
            text-align: center;
            margin: 0 auto;
            font-size: 14px;
        }
        .input-area {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .input-area input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
        }
        .input-area input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .controls { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; }
        .quick-btns { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; }
        .quick-btns button { padding: 12px 30px; font-size: 18px; }
        .eligibility-result {
            display: none;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
            margin-top: 20px;
        }
        .eligibility-result.eligible {
            display: block;
            background: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
        }
        .eligibility-result.not-eligible {
            display: block;
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #dc3545;
        }
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .info-box h3 { color: #2196F3; margin-bottom: 10px; font-size: 14px; }
        .info-box p { font-size: 13px; color: #333; }
        .speaking { animation: pulse 1s infinite; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🎙️</div>
            <h1>QuickRupee Voice Bot</h1>
            <p class="subtitle">Personal Loan Eligibility Screening</p>
        </div>

        <div class="status-bar">
            <div>
                <span class="status-indicator" id="statusIndicator"></span>
                <span id="statusText">Disconnected</span>
            </div>
            <div id="stateText">Ready</div>
        </div>

        <div class="conversation-area" id="conversationArea">
            <div class="message system">Click "Start Conversation" to begin</div>
        </div>

        <div class="quick-btns" id="quickBtns" style="display: none;">
            <button class="btn btn-success" onclick="sendResponse('yes')">👍 YES</button>
            <button class="btn btn-danger" onclick="sendResponse('no')">👎 NO</button>
        </div>

        <div class="input-area" id="inputArea" style="display: none;">
            <input type="text" id="userInput" placeholder="Type your response..." onkeypress="handleKeyPress(event)">
            <button class="btn btn-primary" onclick="sendTypedResponse()">Send</button>
        </div>

        <div class="controls">
            <button class="btn btn-success" id="startBtn" onclick="startConversation()">🎤 Start Conversation</button>
            <button class="btn btn-danger" id="endBtn" onclick="endConversation()" disabled>⏹️ End Call</button>
        </div>

        <div class="eligibility-result" id="eligibilityResult"></div>

        <div class="info-box">
            <h3>💡 How to Use</h3>
            <p>Click YES or NO buttons to answer each question. The bot will speak the questions and responses out loud.</p>
        </div>
    </div>

    <script>
        let ws = null;
        let currentAudio = null;

        function addMessage(text, type) {
            const area = document.getElementById('conversationArea');
            const msg = document.createElement('div');
            msg.className = 'message ' + type;
            msg.textContent = text;
            area.appendChild(msg);
            area.scrollTop = area.scrollHeight;
        }

        function updateStatus(connected, text) {
            const indicator = document.getElementById('statusIndicator');
            document.getElementById('statusText').textContent = text || (connected ? 'Connected' : 'Disconnected');
            if (connected) {
                indicator.classList.add('connected');
            } else {
                indicator.classList.remove('connected');
            }
        }

        function startConversation() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(protocol + '//' + window.location.host + '/ws/chat');

            ws.onopen = () => {
                updateStatus(true, 'Connected');
                document.getElementById('startBtn').disabled = true;
                document.getElementById('endBtn').disabled = false;
                document.getElementById('quickBtns').style.display = 'flex';
                document.getElementById('inputArea').style.display = 'flex';
                document.getElementById('conversationArea').innerHTML = '';
            };

            ws.onmessage = async (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'bot_message') {
                    addMessage(data.text, 'bot');
                    document.getElementById('stateText').textContent = 'State: ' + (data.state || 'unknown');

                    // Play audio if available
                    if (data.audio) {
                        await playAudio(data.audio);
                    }

                    // Check if conversation ended
                    if (data.should_end) {
                        setTimeout(() => {
                            const resultDiv = document.getElementById('eligibilityResult');
                            if (data.is_eligible) {
                                resultDiv.className = 'eligibility-result eligible';
                                resultDiv.innerHTML = '✅ ELIGIBLE<br><small>An agent will call you back within 10 minutes</small>';
                            } else {
                                resultDiv.className = 'eligibility-result not-eligible';
                                resultDiv.innerHTML = '❌ NOT ELIGIBLE<br><small>You do not meet the current criteria</small>';
                            }
                            document.getElementById('quickBtns').style.display = 'none';
                            document.getElementById('inputArea').style.display = 'none';
                        }, 1000);
                    }
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                addMessage('Connection error. Please refresh.', 'system');
            };

            ws.onclose = () => {
                updateStatus(false, 'Disconnected');
            };
        }

        async function playAudio(base64Audio) {
            return new Promise((resolve) => {
                try {
                    if (currentAudio) {
                        currentAudio.pause();
                    }
                    const audio = new Audio('data:audio/mp3;base64,' + base64Audio);
                    currentAudio = audio;
                    audio.onended = resolve;
                    audio.onerror = resolve;
                    audio.play().catch(resolve);
                } catch (e) {
                    console.error('Audio error:', e);
                    resolve();
                }
            });
        }

        function sendResponse(response) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                addMessage(response.toUpperCase(), 'user');
                ws.send(JSON.stringify({ type: 'user_response', text: response }));
            }
        }

        function sendTypedResponse() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (text && ws && ws.readyState === WebSocket.OPEN) {
                addMessage(text, 'user');
                ws.send(JSON.stringify({ type: 'user_response', text: text }));
                input.value = '';
            }
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendTypedResponse();
            }
        }

        function endConversation() {
            if (ws) {
                ws.close();
            }
            document.getElementById('startBtn').disabled = false;
            document.getElementById('endBtn').disabled = true;
            document.getElementById('quickBtns').style.display = 'none';
            document.getElementById('inputArea').style.display = 'none';
            addMessage('Conversation ended', 'system');
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """Simple WebSocket endpoint for chat"""
    await websocket.accept()
    logger.info("New session started")

    state_machine = EligibilityStateMachine()

    try:
        # Send greeting
        greeting = state_machine.start()
        logger.info(f"Bot: {greeting}")

        # Generate TTS for greeting
        audio_data = await text_to_speech(greeting)
        audio_b64 = base64.b64encode(audio_data).decode() if audio_data else None

        await websocket.send_json({
            "type": "bot_message",
            "text": greeting,
            "audio": audio_b64,
            "state": "greeting",
            "should_end": False,
        })

        # Move to first question
        first_question = state_machine.process_response("")
        logger.info(f"Bot: {first_question['message']}")

        # Generate TTS for first question
        audio_data = await text_to_speech(first_question["message"])
        audio_b64 = base64.b64encode(audio_data).decode() if audio_data else None

        await websocket.send_json({
            "type": "bot_message",
            "text": first_question["message"],
            "audio": audio_b64,
            "state": first_question["state"],
            "should_end": False,
        })

        # Conversation loop
        while True:
            message = await websocket.receive_json()

            if message.get("type") == "user_response":
                user_text = message.get("text", "")
                logger.info(f"User: {user_text}")

                # Process response
                result = state_machine.process_response(user_text)

                if not result.get("is_valid", True):
                    logger.info(f"Invalid response: {user_text}")
                else:
                    logger.info(f"Valid response - State: {result['state']}")

                # Generate TTS
                audio_data = await text_to_speech(result["message"])
                audio_b64 = base64.b64encode(audio_data).decode() if audio_data else None

                await websocket.send_json({
                    "type": "bot_message",
                    "text": result["message"],
                    "audio": audio_b64,
                    "state": result["state"],
                    "should_end": result["should_end"],
                    "is_eligible": result.get("is_eligible"),
                })

                if result["should_end"]:
                    logger.info(f"Conversation ended - Eligible: {result.get('is_eligible')}")
                    await asyncio.sleep(2)
                    break

    except WebSocketDisconnect:
        logger.info("Session disconnected")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "simple_demo"}


if __name__ == "__main__":
    uvicorn.run("simple_demo:app", host="0.0.0.0", port=8000, reload=False)
