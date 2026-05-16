#!/usr/bin/env python3
"""
Voice Assistant - Whisper-based Hotword Launcher
=================================================
Runs local Whisper in continuous loop, listens for hotwords, and executes commands.

Features:
- Local Whisper inference (no cloud API)
- Configurable hotword detection
- Command mapping to local scripts
- Transcript logging
- Action logging
- Low-latency audio processing

Usage:
    python run_voice.py                          # Start voice assistant
    python run_voice.py --device 0               # Use specific audio device
    python run_voice.py --model tiny             # Use tiny model (fastest)
    python run_voice.py --no-execute             # Listen only, don't execute
    python run_voice.py --verbose                # Verbose output

Dependencies:
    - openai-whisper
    - pyaudio
    - torch (for Whisper)
"""

import argparse
import audioop
import json
import logging
import os
import signal
import subprocess
import sys
import time
from collections import deque
from pathlib import Path
from typing import Deque, Dict, Optional, Tuple

try:
    import torch
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: Whisper not installed. Install with: pip install openai-whisper torch")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: PyAudio not installed. Install with: pip install pyaudio")

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
COMMANDS_FILE = BASE_DIR / "commands.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "voice.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class AudioRecorder:
    """Audio recorder with VAD (Voice Activity Detection)."""

    def __init__(self, device_index: Optional[int] = None, chunk_size: int = 1024):
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.device_index = device_index
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False

        # VAD parameters
        self.energy_threshold = 1000
        self.energy_history: Deque = deque(maxlen=100)
        self.silence_threshold = 200
        self.speech_timeout = 2.0
        self.last_speech_time = 0

    def get_available_devices(self) -> list:
        """Get list of available audio input devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                devices.append({
                    "index": i,
                    "name": info["name"],
                    "channels": info["maxInputChannels"],
                })
        return devices

    def calibrate(self, duration: float = 3.0) -> int:
        """Calibrate microphone for ambient noise."""
        logger.info(f"Calibrating microphone for {duration} seconds...")
        energies = []

        with self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index,
        ) as stream:
            start_time = time.time()
            while time.time() - start_time < duration:
                data = stream.read(self.chunk_size)
                energy = audioop.rms(data, 2)
                energies.append(energy)

        avg_energy = sum(energies) / len(energies) if energies else 1000
        self.energy_threshold = int(avg_energy * 1.5)
        logger.info(f"Calibrated energy threshold: {self.energy_threshold}")
        return self.energy_threshold

    def record_segment(self, max_duration: float = 10.0) -> bytes:
        """Record a speech segment with VAD."""
        frames = []
        start_time = time.time()
        speaking = False

        logger.info("Listening for speech...")

        while time.time() - start_time < max_duration:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            energy = audioop.rms(data, 2)
            self.energy_history.append(energy)

            avg_energy = sum(self.energy_history) / len(self.energy_history)

            if energy > self.energy_threshold:
                if not speaking:
                    logger.info("Speech detected, recording...")
                    speaking = True
                frames.append(data)
                self.last_speech_time = time.time()
            elif speaking:
                if time.time() - self.last_speech_time > self.speech_timeout:
                    logger.info("Speech ended.")
                    break
                frames.append(data)

        return b"".join(frames)

    def start(self):
        """Start the audio stream."""
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index,
        )
        self.running = True
        logger.info(f"Audio recording started (device: {self.device_index})")

    def stop(self):
        """Stop the audio stream."""
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()


class WhisperProcessor:
    """Whisper model processor for speech recognition."""

    def __init__(self, model_name: str = "base", device: Optional[str] = None):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None

        if not WHISPER_AVAILABLE:
            logger.error("Whisper not available. Please install openai-whisper and torch.")
            sys.exit(1)

        logger.info(f"Loading Whisper model '{model_name}' on {self.device}...")
        self.model = whisper.load_model(model_name).to(self.device)
        logger.info("Whisper model loaded successfully.")

    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text."""
        import numpy as np

        # Convert audio bytes to numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Run transcription
        result = self.model.transcribe(
            audio_np,
            fp16=(self.device == "cuda"),
            language="en",
        )

        text = result["text"].strip()
        return text


class CommandExecutor:
    """Executes commands based on voice input."""

    def __init__(self, commands_file: Path):
        self.commands_file = commands_file
        self.commands: Dict = {}
        self.transcript_log: Deque = deque(maxlen=1000)
        self.action_log: Deque = deque(maxlen=1000)
        self.load_commands()

    def load_commands(self):
        """Load commands from JSON file."""
        if self.commands_file.exists():
            with open(self.commands_file, "r") as f:
                self.commands = json.load(f)
            logger.info(f"Loaded {len(self.commands)} voice commands")
        else:
            logger.warning(f"Commands file not found: {self.commands_file}")
            self.commands = {}

    def get_best_match(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Find best command match for transcribed text."""
        text_lower = text.lower()

        best_match = None
        best_score = 0

        for trigger, command_info in self.commands.items():
            trigger_lower = trigger.lower()
            if trigger_lower in text_lower:
                score = len(trigger_lower) / len(text_lower)
                if score > best_score:
                    best_match = (trigger, command_info, score)

        return best_match

    def execute_command(self, command_info: Dict, trigger: str) -> bool:
        """Execute a command."""
        cmd_type = command_info.get("type", "script")
        cmd_value = command_info.get("command", "")
        cwd = command_info.get("cwd", str(BASE_DIR))

        logger.info(f"Executing command: {cmd_value}")

        try:
            if cmd_type == "script":
                # Run a script file
                script_path = BASE_DIR / cmd_value
                if script_path.exists():
                    subprocess.run(
                        [sys.executable, str(script_path)],
                        cwd=cwd,
                        check=True,
                    )
                else:
                    subprocess.run(["bash", cmd_value], cwd=cwd, check=True)

            elif cmd_type == "launcher":
                # Use launcher.py
                subprocess.run(
                    [sys.executable, str(BASE_DIR / "launch.py")] + command_info.get("args", []),
                    cwd=cwd,
                    check=True,
                )

            elif cmd_type == "shell":
                # Run shell command
                subprocess.run(cmd_value, shell=True, cwd=cwd, check=True)

            # Log successful execution
            self.action_log.append({
                "timestamp": time.time(),
                "trigger": trigger,
                "command": cmd_value,
                "status": "success",
            })
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            self.action_log.append({
                "timestamp": time.time(),
                "trigger": trigger,
                "command": cmd_value,
                "status": "failed",
                "error": str(e),
            })
            return False

    def log_transcript(self, text: str, action_taken: Optional[str] = None):
        """Log a transcription."""
        entry = {
            "timestamp": time.time(),
            "text": text,
            "action": action_taken,
        }
        self.transcript_log.append(entry)

        # Also write to file
        log_file = LOG_DIR / "voice_transcripts.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")


class VoiceAssistant:
    """Main voice assistant class."""

    def __init__(
        self,
        model: str = "base",
        device: Optional[int] = None,
        no_execute: bool = False,
        calibrate: bool = False,
    ):
        self.no_execute = no_execute
        self.running = False

        # Initialize components
        self.recorder = AudioRecorder(device_index=device)
        self.processor = WhisperProcessor(model_name=model)
        self.executor = CommandExecutor(COMMANDS_FILE)

        # Handle calibration
        if calibrate:
            self.recorder.calibrate()

    def start(self):
        """Start the voice assistant."""
        self.running = True

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("=" * 50)
        logger.info("🎙️  Voice Assistant Started")
        logger.info("Say a hotword to trigger a command...")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 50)

        # Start recording
        self.recorder.start()

        try:
            while self.running:
                # Record audio segment
                audio_data = self.recorder.record_segment()

                if not audio_data:
                    continue

                # Transcribe
                text = self.processor.transcribe(audio_data)

                if not text:
                    continue

                logger.info(f"🎤 Heard: {text}")

                # Log transcript
                self.executor.log_transcript(text)

                # Find and execute command
                match = self.executor.get_best_match(text)

                if match:
                    trigger, command_info, score = match
                    logger.info(f"🔗 Matched trigger: '{trigger}' (score: {score:.2f})")

                    if not self.no_execute:
                        self.executor.execute_command(command_info, trigger)
                        self.executor.log_transcript(text, trigger)
                    else:
                        logger.info("Would execute: " + command_info.get("command", ""))

        except Exception as e:
            logger.error(f"Voice assistant error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the voice assistant."""
        self.running = False
        self.recorder.stop()
        logger.info("Voice assistant stopped.")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Received shutdown signal...")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Voice Assistant - Whisper-based Hotword Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_voice.py                    Start voice assistant
  python run_voice.py --model tiny       Use tiny model (faster)
  python run_voice.py --device 1         Use audio device 1
  python run_voice.py --calibrate        Calibrate microphone
  python run_voice.py --no-execute       Listen only, don't execute
  python run_voice.py --verbose          Verbose output
        """,
    )

    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Audio device index (default: default device)",
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Calibrate microphone for ambient noise",
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Listen and log only, don't execute commands",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio input devices",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.list_devices:
        recorder = AudioRecorder()
        devices = recorder.get_available_devices()
        print("\nAvailable Audio Input Devices:")
        for i, dev in enumerate(devices):
            print(f"  {i}: {dev['name']} ({dev['channels']} channels)")
        return

    if not PYAUDIO_AVAILABLE:
        logger.error("PyAudio is required. Install with: pip install pyaudio")
        sys.exit(1)

    assistant = VoiceAssistant(
        model=args.model,
        device=args.device,
        no_execute=args.no_execute,
        calibrate=args.calibrate,
    )
    assistant.start()


if __name__ == "__main__":
    main()
