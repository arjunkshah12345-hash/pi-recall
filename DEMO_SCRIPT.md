# Demo Script

Target length: 2-4 minutes.

## 0:00 - Hook

"Alexa remembers commands. Pi Recall remembers context. It is a Raspberry Pi voice assistant backed by Supermemory Local, so it can use something I said weeks ago in a future conversation."

## 0:20 - Show The Build

Show the Pi 5, mic, and speaker. Say:

"Wake word detection runs locally with Porcupine. The memory layer is Supermemory Local running on localhost, not the hosted API. Groq handles free-tier speech, language, and voice output."

## 0:45 - Memory Moment

Say:

"Hey Pi, remember that my garage door sensor has been flaky since the storm, and I should check the battery before replacing it."

Show logs where the transcript is written to the local Supermemory server.

## 1:20 - Recall Moment

Say:

"Hey Pi, what did I say about the garage door sensor?"

Expected answer:

It should mention the storm, the flaky garage sensor, and checking the battery first.

## 1:50 - Tool Moment

Say:

"Hey Pi, add a reminder or calendar task to check the garage sensor battery tomorrow."

Show the Composio tool path. If the account is not connected live, show the configured code path and explain the OAuth step.

## 2:30 - Why Supermemory

"The product only works because memory is first-class. Every utterance becomes durable context, and the assistant retrieves only the relevant pieces when it needs them."

## 3:00 - Close

"This is not a chatbot on a Pi. It is a local-memory voice agent that can become the context layer for a house."
