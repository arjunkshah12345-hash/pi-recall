# Pi Recall

An always-on Raspberry Pi voice assistant that remembers what you said weeks ago.

## What It Does

- Wake word: `Hey Pi` through offline Porcupine.
- Speech-to-text: Groq Whisper.
- Memory: every user utterance is written to Supermemory Local.
- Recall: each turn queries Supermemory profile/search context before answering.
- Tools: optional Composio hook for Gmail, calendar, GitHub, Slack, home tooling, etc.
- Voice response: Groq Orpheus TTS played through the Pi speaker.

## Why It Matters

Most voice assistants are stateless command routers. Pi Recall is built around long-term memory: it can remember preferences, ongoing projects, household details, and old conversations without sending that memory layer to a hosted database.

## Install

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[pi,dev]"
cp .env.example .env
```

Install and run Supermemory Local:

```bash
curl -fsSL https://supermemory.ai/install | bash
npx supermemory local
```

Copy the local key printed by Supermemory Local into `.env` as `SUPERMEMORY_LOCAL_KEY`.
The assistant talks to `SUPERMEMORY_LOCAL_URL`, which defaults to `http://localhost:6767`.

Create a custom `Hey Pi` Porcupine wake word in Picovoice Console, download the Raspberry Pi/Linux `.ppn`, and set `PORCUPINE_KEYWORD_PATH`.

## Run

```bash
source .venv/bin/activate
pi-assistant-doctor
pi-assistant
```

For laptop development or judge review without Pi hardware:

```bash
pi-assistant-console
pi-assistant-demo
```

## Hardware Notes

Use a USB mic or ReSpeaker-style array for input and a 3.5mm/HDMI/USB speaker for output. If Linux picks the wrong device, list devices with:

```bash
python -m sounddevice
```

Then set `INPUT_DEVICE` and `OUTPUT_DEVICE` in `.env`.

## Tool Access

Set `COMPOSIO_API_KEY`, `COMPOSIO_USER_ID`, and `COMPOSIO_TOOLKITS`. Keep `COMPOSIO_TOOLKITS` narrow for live demos. Add house hardware through Composio/custom tools only after you have an allowlist and confirmation flow.

Connect tools from the Pi shell:

```bash
composio add github
composio add gmail
composio add googlecalendar
```

## Run On Boot

```bash
bash scripts/install_pi_service.sh
journalctl --user -u pi-assistant.service -f
```

## Why This Shape

The wake-word loop stays local and cheap. Only the bounded utterance after `Hey Pi` goes to STT. Every transcript is written to the local Supermemory process before the answer is generated, so future turns can recall old details.

## Supermemory Local Only

Pi Recall uses the self-hosted/local Supermemory server. It does not use the hosted Supermemory API. The local process exposes a localhost HTTP interface, and this app points at that interface through `SUPERMEMORY_LOCAL_URL`.

## Free API Stack

This project uses Groq instead of OpenAI for inference:

- LLM: `llama-3.3-70b-versatile`
- STT: `whisper-large-v3-turbo`
- TTS: `canopylabs/orpheus-v1-english`

Set `GROQ_API_KEY` in `.env`. Groq has a free developer tier, but rate limits can change.

## Submission Assets

- [HACKATHON.md](./HACKATHON.md): judge-facing project writeup.
- [DEMO_SCRIPT.md](./DEMO_SCRIPT.md): 2-4 minute demo video outline.
- [ARCHITECTURE.md](./ARCHITECTURE.md): system diagram and data flow.
