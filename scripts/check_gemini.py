# check_gemini.py  (run in your venv; reads GEMINI_API_KEY from the repo-root .env)
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
client = genai.Client()
for m in client.models.list():
    if "generateContent" in m.supported_actions:
        print(m.name)
