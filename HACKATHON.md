# Pi Recall Hackathon Submission

## One-Liner

Pi Recall is a Raspberry Pi voice assistant that uses Supermemory Local as its long-term memory, so it can remember what you said weeks ago and use that context in future spoken conversations.

Website: https://pi-recall.vercel.app  
GitLab: https://gitlab.com/arjunkshah/pi-recall

## Problem

Voice assistants are useful for commands but weak at continuity. They forget preferences, home quirks, ongoing projects, and prior instructions unless every integration stores its own state. That makes them feel transactional instead of personal.

## Solution

Pi Recall turns every spoken user utterance into Supermemory Local context. When the user asks a new question, the assistant retrieves profile facts and relevant memories from the local Supermemory process before generating a response. It runs as an always-on Pi service with a local wake word, free-tier Groq inference, voice output, and optional Composio tools.

## Supermemory Local Usage

- Every user transcript is ingested into the self-hosted Supermemory Local server.
- A single `SUPERMEMORY_CONTAINER` scopes the user's home memory graph.
- Each turn calls the local server's profile endpoint with the current transcript as `q`.
- Static profile, dynamic profile, and relevant search memories are injected into the model context.
- Memory remains useful even when the immediate conversation is gone.
- The hosted Supermemory API is not used.

## Tech Stack

- Raspberry Pi 5
- Porcupine wake word detection
- Supermemory Local
- Groq Whisper STT
- Groq chat completions
- Groq Orpheus TTS
- Composio tools
- Python, sounddevice, soundfile
- systemd user service

## What Makes It Strong

- It is embodied: a real voice assistant on hardware, not just a web chat.
- It uses Supermemory as the core product primitive, not as an afterthought.
- It has a no-hardware console/demo path for judges.
- It is free-tier friendly: no OpenAI API billing required.
- It has a clear expansion path into home automation, calendar, reminders, and household operations.

## Run Commands

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[pi,dev]"
cp .env.example .env
npx supermemory local
pi-assistant-doctor
pi-assistant-demo
pi-assistant-console
pi-assistant
```

## Submission Checklist

- Working source code: yes
- Setup instructions: yes
- Architecture overview: yes
- Demo path without Pi hardware: yes
- Real Pi wake-word path: yes
- Supermemory Local integration: yes
- Hosted Supermemory API dependency: no
- Tool integration path: yes
- Demo video: still needed

## Future Work

- Add local VAD-based end-of-speech detection instead of fixed recording windows.
- Add hardware tool confirmations for lights, locks, thermostats, and garage controls.
- Add a memory dashboard for inspecting what the assistant knows.
- Add multi-user voice profiles so each household member gets a separate memory graph.
