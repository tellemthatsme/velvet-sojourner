# Voice Assistant Documentation

## Overview

The Voice Assistant module uses OpenAI's Whisper model for local speech recognition. It listens for hotwords and executes configured commands.

## Features

- Local Whisper inference (no cloud API calls after initial download)
- Configurable hotword detection
- Command mapping to any script
- Transcript logging
- Action logging
- Low-latency audio processing

## Requirements

- Python 3.8+
- FFmpeg (for audio processing)
- PyAudio
- torch
- openai-whisper

## Installation

```bash
# Install audio dependencies
# macOS
brew install ffmpeg portaudio

# Ubuntu/Debian
sudo apt install ffmpeg portaudio19-dev

# Windows
winget install ffmpeg

# Install Python packages
pip install pyaudio torch openai-whisper
```

## Usage

### Basic

```bash
python run_voice.py
```

### With Options

```bash
# Use smaller model (faster)
python run_voice.py --model tiny

# Calibrate microphone
python run_voice.py --calibrate

# List audio devices
python run_voice.py --list-devices

# Listen only (no execution)
python run_voice.py --no-execute
```

## Configuration

Edit `commands.json` to map voice triggers to actions:

```json
{
  "start voice": {
    "type": "launcher",
    "command": "voice",
    "description": "Start voice assistant"
  },
  "sync github": {
    "type": "launcher",
    "command": "sync-github",
    "description": "Sync GitHub repositories"
  }
}
```

### Command Types

- `launcher`: Run via launch.py
- `script`: Run Python script directly
- `shell`: Run shell command

## Hotword Detection

The module uses keyword matching. Say a phrase that triggers a command:

```
"Hey assistant, sync github"
```

The module will match "sync github" and execute the configured command.

## Audio Device Selection

```bash
# List available devices
python run_voice.py --list-devices

# Use specific device (index from list)
python run_voice.py --device 1
```

## Troubleshooting

### No Audio Input

1. Check microphone permissions
2. Run `python run_voice.py --list-devices` to verify detection
3. Try calibrating: `python run_voice.py --calibrate`

### Poor Recognition

1. Reduce background noise
2. Speak clearly and closer to microphone
3. Try a larger Whisper model

### Model Loading Fails

Ensure torch is installed correctly:
```bash
pip install torch torchvision torchaudio
```
