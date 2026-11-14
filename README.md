# GrizzHelper 🐻

A Clippy-style bear for Windows 11 that does things on your PC for you. Type a request (or hold
a key and say it), and GrizzHelper plans it with an AI, takes real actions in Windows apps, then
answers in its speech bubble and out loud.

Built for people who can't comfortably use a mouse and keyboard (RSI, motor impairments,
injuries). Hack the Nest 2026.

## How it works

```
text box / push-to-talk ──► ElevenLabs speech-to-text
                                   │
                                   ▼
          agent loop: gpt-oss-20b (vLLM) + tool calling
                                   │
                                   ▼
   Windows actions: UI Automation ► keyboard/mouse ► Gemini vision (last resort)
                                   │
                                   ▼
          reply in the bubble ──► ElevenLabs text-to-speech
```

The mascot window (Electron) and the Python backend talk over a local WebSocket
(`ws://127.0.0.1:8765`) using JSON messages: `{"type": "...", "payload": {...}}`.
The message types are listed in `backend/protocol.py` and mirrored in `mascot/protocol.js`.

## Setup (Windows 11)

You need: **Python 3.11+** (check with `py -0`), **Node.js 20+**, and Git.

Commands are for PowerShell (VS Code's default terminal), run from the repo root.

1. **Python environment**

   ```powershell
   py -3.11 -m venv .venv          # any 3.11+ works: use a version `py -0` lists
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   If PowerShell says *"running scripts is disabled on this system"*, run this once, then retry:
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

2. **Secrets**

   ```powershell
   copy .env.example .env
   ```

   Fill in `.env` (ask Nora privately for the model server values). `.env` is gitignored.
   Never commit it, and never paste keys or the server URL in Discord or GitHub.

3. **Smoke test**: checks this laptop can reach the model and get a tool call back.

   ```powershell
   python scripts/smoke_test.py
   ```

   It should end with `PASS`.

4. **Mascot window**

   ```powershell
   cd mascot
   npm install
   npm start
   ```

5. **Backend** (once it's implemented), in a second terminal with the venv active:

   ```powershell
   python -m backend.server        # bridge to the mascot
   python -m backend.agent.loop    # or: agent only, in the terminal
   ```

   Always run backend code from the repo root with `python -m ...` so `import backend...` works.

## Model server (Brev)

gpt-oss-20b runs on vLLM, which serves an OpenAI-compatible API. Tool calling needs two flags:

```bash
vllm serve openai/gpt-oss-20b --tool-call-parser openai --enable-auto-tool-choice --api-key <choose-a-key>
```

Only `tool_choice="auto"` is supported. Guide:
https://docs.vllm.ai/projects/recipes/en/latest/OpenAI/GPT-OSS.html

## Project layout

```
backend/
  server.py          WebSocket bridge to the mascot window
  protocol.py        message types (mirrored in mascot/protocol.js)
  agent/             loop.py (tool-calling loop), prompt.py, tool_schemas.py
  tools/             apps, ui (pywinauto UIA), keyboard_mouse, screen (mss + Gemini),
                     files, settings (ms-settings pages), web (Exa, optional)
  voice/             hotkey.py (push-to-talk), stt.py, tts.py (ElevenLabs)
mascot/              Electron, plain JavaScript: main.js, preload.js, index.html,
                     renderer.js, style.css, protocol.js, assets/
scripts/smoke_test.py
docs/test-log.md
```

## Team

| Area | Owner |
|---|---|
| `backend/agent/`, `tools/apps.py`, `tools/ui.py`, `tools/keyboard_mouse.py` | Jay |
| `mascot/`, `backend/server.py`, `backend/voice/` | Michael |
| Brev model server, `tools/screen.py`, `tools/files.py`, `tools/web.py` | Nora |
| Mascot art, `tools/settings.py`, `docs/test-log.md`, Devpost, demo | Sarahi |

`main` must always run. Work on `name/feature` branches and open small PRs.
