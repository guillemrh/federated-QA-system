import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MODEL = "models/gemini-2.5-flash"

TRANSFORMER_MODEL = "all-MiniLM-L6-v2"

ORCHESTRATOR_URL = "http://localhost:8000/ask"
