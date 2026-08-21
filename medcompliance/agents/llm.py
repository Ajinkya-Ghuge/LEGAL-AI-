"""Shared LLM — loads Gemini API key from .env file or environment."""
import os, time, warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def _load_key() -> str:
    # 1. Already in environment
    key = os.environ.get("GEMINI_API_KEY", "")
    if key and "placeholder" not in key and len(key) > 10:
        return key
    # 2. Read from .env in this folder or parent folder
    for search_dir in [os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))]:
        env_path = os.path.join(search_dir, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and len(val) > 10 and "placeholder" not in val:
                            return val
    return ""

GEMINI_API_KEY = _load_key()

MODELS = [
    "gemini-2.5-flash-lite",   # lightest quota — try first
    "gemini-2.0-flash-lite",   # very low quota usage
    "gemini-2.0-flash",        # fast, generous quota
    "gemini-flash-lite-latest", # alias fallback
    "gemini-2.5-flash",        # main model (may hit quota)
]

def call_gemini(prompt: str, fallback: str = "") -> str:
    if not GEMINI_API_KEY:
        return fallback or "[Error: GEMINI_API_KEY not set in .env]"
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
    except ImportError:
        return fallback or "[Error: google-generativeai not installed]"
    last_err = ""
    for model_name in MODELS:
        try:
            resp = genai.GenerativeModel(model_name).generate_content(prompt)
            if resp.text:
                return resp.text
        except Exception as e:
            last_err = str(e)
            if "leaked" in last_err.lower() or "API_KEY_INVALID" in last_err or "403" in last_err:
                break
            if "429" in last_err or "quota" in last_err.lower():
                time.sleep(3)
                continue
    return fallback or f"[AI Error: {last_err[:120]}]"
