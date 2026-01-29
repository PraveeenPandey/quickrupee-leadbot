"""
QuickRupee Voice Bot - Demo Server (No Twilio Required)
Browser-based demo for local testing and interviews
"""
import asyncio
import logging
import json
import base64
import httpx
from contextlib import asynccontextmanager
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

from config import settings
from state_machine import EligibilityStateMachine
from openai_realtime import OpenAIRealtimeClient


async def text_to_speech(text: str) -> Optional[bytes]:
    """Convert text to speech using OpenAI TTS API (reliable, non-realtime)"""
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
                logging.error(f"TTS API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logging.error(f"TTS error: {e}")
        return None


# TTS Cache for pre-generated audio
tts_cache: Dict[str, bytes] = {}


async def get_cached_tts(text: str) -> Optional[bytes]:
    """Get TTS from cache or generate if not cached"""
    if text in tts_cache:
        return tts_cache[text]

    # Generate and cache
    audio = await text_to_speech(text)
    if audio:
        tts_cache[text] = audio
    return audio


async def preload_tts_cache():
    """Pre-generate TTS for all known scripts at startup"""
    from state_machine import EligibilityStateMachine, State

    scripts_to_cache = [
        EligibilityStateMachine.SCRIPTS[State.GREETING],
        EligibilityStateMachine.SCRIPTS[State.ASK_EMPLOYMENT],
        EligibilityStateMachine.SCRIPTS[State.ASK_SALARY],
        EligibilityStateMachine.SCRIPTS[State.ASK_CITY],
        EligibilityStateMachine.SCRIPTS[State.ELIGIBLE],
        EligibilityStateMachine.SCRIPTS[State.NOT_ELIGIBLE],
        # Invalid response clarification
        "I'm sorry, I didn't understand. Please say Yes or No. " + EligibilityStateMachine.SCRIPTS[State.ASK_EMPLOYMENT],
        "I'm sorry, I didn't understand. Please say Yes or No. " + EligibilityStateMachine.SCRIPTS[State.ASK_SALARY],
        "I'm sorry, I didn't understand. Please say Yes or No. " + EligibilityStateMachine.SCRIPTS[State.ASK_CITY],
    ]

    logging.info(f"Pre-loading TTS cache for {len(scripts_to_cache)} scripts...")

    for script in scripts_to_cache:
        audio = await text_to_speech(script)
        if audio:
            tts_cache[script] = audio
            logging.info(f"Cached: {script[:50]}...")

    logging.info(f"TTS cache loaded with {len(tts_cache)} entries")

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Active sessions
sessions: Dict[str, EligibilityStateMachine] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("QuickRupee Voice Bot Demo starting up...")
    logger.info(f"OpenAI API Key configured: {bool(settings.OPENAI_API_KEY)}")
    logger.info(f"Min salary threshold: ₹{settings.MIN_SALARY}")
    logger.info(f"Eligible cities: {settings.ELIGIBLE_CITIES}")

    # Pre-load TTS cache for instant responses
    await preload_tts_cache()

    logger.info("=" * 60)
    logger.info("🎙️  Demo Mode - No Twilio Required")
    logger.info("📱 Open http://localhost:8000 in your browser")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("QuickRupee Voice Bot Demo shutting down...")
    sessions.clear()
    tts_cache.clear()


# FastAPI app with lifespan
app = FastAPI(
    title="QuickRupee Voice Bot - Demo",
    description="Browser-based demo without Twilio",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Serve the demo interface"""
    with open("static/demo.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(sessions),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "mode": "demo",
    }


@app.websocket("/demo/voice/{session_id}")
async def demo_voice_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for browser-based audio streaming
    Connects browser microphone directly to OpenAI Realtime API
    """
    await websocket.accept()
    logger.info(f"Demo session started: {session_id}")

    # Initialize state machine
    state_machine = EligibilityStateMachine()
    sessions[session_id] = state_machine

    # OpenAI Realtime client
    openai_client: Optional[OpenAIRealtimeClient] = None

    # Control when to process transcripts (ignore bot's own voice)
    listening_for_user = False

    try:
        # Callbacks for OpenAI events
        async def on_transcript(text: str):
            """Handle transcribed user speech"""
            nonlocal listening_for_user

            logger.info(f"Transcript received: {text}")

            # Ignore transcripts until we're ready for user input
            if not listening_for_user:
                logger.info("Ignoring transcript (not listening for user yet)")
                return

            logger.info(f"User said: {text}")

            # Send transcript to frontend
            await websocket.send_json({
                "type": "transcript",
                "text": text,
                "role": "user"
            })

            # Process through state machine
            result = state_machine.process_response(text)

            if not result.get('is_valid', True):
                logger.info(f"Invalid response received: '{text}' - Re-asking question")
            else:
                logger.info(f"Valid response - State: {result['state']}, Should end: {result['should_end']}")

            # Send state update to frontend
            await websocket.send_json({
                "type": "state_update",
                "state": result['state'],
                "should_end": result['should_end'],
                "is_eligible": result.get('is_eligible')
            })

            # Wait a brief moment for OpenAI to finish processing user's audio input
            await asyncio.sleep(0.3)

            # Temporarily stop listening while bot speaks
            listening_for_user = False
            logger.info("Bot speaking - temporarily stopped listening")

            # Tell frontend to mute microphone while bot speaks
            await websocket.send_json({"type": "mute_mic"})

            # Clear any audio in OpenAI's buffer
            await openai_client.clear_audio_buffer()

            # Send bot response via TTS (using standard TTS API, not Realtime)
            if result["message"]:
                # Send message text to frontend
                await websocket.send_json({
                    "type": "bot_message",
                    "text": result["message"]
                })

                # Get TTS from cache (instant) or generate
                audio_data = await get_cached_tts(result["message"])
                if audio_data:
                    # Send MP3 audio to frontend
                    await websocket.send_json({
                        "type": "audio_mp3",
                        "data": base64.b64encode(audio_data).decode('utf-8')
                    })

                # Resume listening for next user input (if conversation continues)
                if not result["should_end"]:
                    # Tell frontend to unmute after audio finishes
                    await websocket.send_json({"type": "unmute_mic"})
                    listening_for_user = True
                    logger.info("✅ Bot finished generating speech - will listen after playback")

            # End call if conversation is complete
            if result["should_end"]:
                await asyncio.sleep(5)  # Wait for TTS to complete
                await websocket.send_json({
                    "type": "end_conversation",
                    "is_eligible": result.get('is_eligible')
                })

        async def on_error(error: str):
            """Handle OpenAI errors"""
            logger.error(f"OpenAI error: {error}")
            await websocket.send_json({
                "type": "error",
                "message": error
            })

        # Connect to OpenAI Realtime API (STT only)
        openai_client = OpenAIRealtimeClient(
            on_transcript=on_transcript,
            on_error=on_error,
        )
        await openai_client.connect()

        # Send ready signal to frontend
        await websocket.send_json({
            "type": "ready",
            "message": "Connected to voice bot"
        })

        # Mute mic during initial bot speech
        await websocket.send_json({"type": "mute_mic"})

        # Clear any audio buffer
        await openai_client.clear_audio_buffer()

        # Start conversation with greeting
        greeting = state_machine.start()
        await websocket.send_json({
            "type": "bot_message",
            "text": greeting
        })

        # Get TTS for greeting from cache (instant)
        greeting_audio = await get_cached_tts(greeting)
        if greeting_audio:
            await websocket.send_json({
                "type": "audio_mp3",
                "data": base64.b64encode(greeting_audio).decode('utf-8')
            })

        # Transition from GREETING to ASK_EMPLOYMENT
        first_question = state_machine.process_response("")
        if first_question["message"]:
            await websocket.send_json({
                "type": "bot_message",
                "text": first_question["message"]
            })

            # Get TTS for first question from cache (instant)
            question_audio = await get_cached_tts(first_question["message"])
            if question_audio:
                await websocket.send_json({
                    "type": "audio_mp3",
                    "data": base64.b64encode(question_audio).decode('utf-8')
                })

            # Tell frontend to unmute after audio finishes playing
            await websocket.send_json({"type": "unmute_mic"})
            listening_for_user = True
            logger.info("✅ First question sent - will listen after playback")

        # Process incoming messages from browser
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if msg_type == "audio":
                # Incoming audio from browser microphone
                audio_b64 = message.get("data", "")
                if audio_b64:
                    audio_bytes = base64.b64decode(audio_b64)
                    await openai_client.send_audio(audio_bytes)

            elif msg_type == "audio_end":
                # User stopped speaking
                await openai_client.commit_audio()

            elif msg_type == "ping":
                # Keep-alive
                await websocket.send_json({"type": "pong"})

            elif msg_type == "end":
                # User ended conversation
                break

    except WebSocketDisconnect:
        logger.info(f"Demo session disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Error in demo session: {e}", exc_info=True)
    finally:
        # Cleanup
        if openai_client:
            await openai_client.close()
        if session_id in sessions:
            del sessions[session_id]
        logger.info(f"Cleaned up demo session: {session_id}")


if __name__ == "__main__":
    uvicorn.run(
        "demo_server:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
