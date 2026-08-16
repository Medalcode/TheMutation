import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(";") if o.strip()]
ENV = os.getenv("ENV", "development")
REQUEST_SIZE_LIMIT = int(os.getenv("REQUEST_SIZE_LIMIT", "1048576"))
REDIS_URL = os.getenv("REDIS_URL")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
