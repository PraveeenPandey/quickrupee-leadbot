"""
OpenAI Realtime API Integration
Handles WebSocket communication with OpenAI's Realtime API for speech-to-text
"""
import asyncio
import json
import base64
import logging
from typing import Optional, Callable
import websockets
from config import settings

logger = logging.getLogger(__name__)


class OpenAIRealtimeClient:
    """
    Client for OpenAI Realtime API (STT only)
    TTS is handled by standard OpenAI TTS API for reliability
    """

    def __init__(
        self,
        on_transcript: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize Realtime API client for speech-to-text

        Args:
            on_transcript: Callback for transcribed text
            on_error: Callback for errors
        """
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.on_transcript = on_transcript
        self.on_error = on_error
        self.is_connected = False
        self._receive_task: Optional[asyncio.Task] = None

    async def connect(self):
        """Establish WebSocket connection to OpenAI Realtime API"""
        try:
            url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1",
            }

            self.ws = await websockets.connect(url, extra_headers=headers)
            self.is_connected = True
            logger.info("Connected to OpenAI Realtime API")

            await self._configure_session()
            self._receive_task = asyncio.create_task(self._receive_messages())

        except Exception as e:
            logger.error(f"Failed to connect to OpenAI Realtime API: {e}")
            if self.on_error:
                await self.on_error(str(e))
            raise

    async def _configure_session(self):
        """Configure the Realtime API session for transcription only"""
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "Transcribe user speech accurately.",
                "voice": settings.VOICE,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 600,
                    "create_response": False,
                },
                "temperature": 0.6,
            },
        }
        await self.ws.send(json.dumps(config))
        logger.info("Session configured for transcription")

    async def _receive_messages(self):
        """Continuously receive and process messages from OpenAI"""
        try:
            async for message in self.ws:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            if self.on_error:
                await self.on_error(str(e))

    async def _handle_message(self, message: str):
        """Handle incoming message from OpenAI"""
        try:
            data = json.loads(message)
            event_type = data.get("type")

            if event_type == "conversation.item.input_audio_transcription.completed":
                transcript = data.get("transcript", "")
                logger.info(f"User said: {transcript}")
                if self.on_transcript:
                    await self.on_transcript(transcript)

            elif event_type == "error":
                error_msg = data.get("error", {}).get("message", "Unknown error")
                logger.error(f"OpenAI error: {error_msg}")
                if self.on_error:
                    await self.on_error(error_msg)

            elif event_type == "session.created":
                logger.info("Session created successfully")

            elif event_type == "session.updated":
                logger.info("Session updated successfully")

            elif event_type == "input_audio_buffer.speech_started":
                logger.info("Speech detected - user started speaking")

            elif event_type == "input_audio_buffer.speech_stopped":
                logger.info("Speech ended - user stopped speaking")

            elif event_type == "input_audio_buffer.committed":
                logger.info("Audio buffer committed for transcription")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def send_audio(self, audio_data: bytes):
        """Send audio data to OpenAI for transcription"""
        if not self.is_connected or not self.ws:
            return

        try:
            audio_b64 = base64.b64encode(audio_data).decode("utf-8")
            event = {
                "type": "input_audio_buffer.append",
                "audio": audio_b64,
            }
            await self.ws.send(json.dumps(event))
        except Exception as e:
            logger.error(f"Error sending audio: {e}")

    async def commit_audio(self):
        """Signal that audio input is complete"""
        if not self.is_connected or not self.ws:
            return

        try:
            event = {"type": "input_audio_buffer.commit"}
            await self.ws.send(json.dumps(event))
        except Exception as e:
            logger.error(f"Error committing audio: {e}")

    async def clear_audio_buffer(self):
        """Clear the input audio buffer"""
        if not self.is_connected or not self.ws:
            return

        try:
            event = {"type": "input_audio_buffer.clear"}
            await self.ws.send(json.dumps(event))
        except Exception as e:
            logger.error(f"Error clearing audio buffer: {e}")

    async def close(self):
        """Close the WebSocket connection"""
        if self._receive_task:
            self._receive_task.cancel()

        if self.ws:
            await self.ws.close()
            self.is_connected = False
            logger.info("Closed OpenAI Realtime API connection")
