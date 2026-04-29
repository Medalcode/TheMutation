import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(";")
ENV = os.getenv("ENV", "development")
REQUEST_SIZE_LIMIT = int(os.getenv("REQUEST_SIZE_LIMIT", "1048576"))
REDIS_URL = os.getenv("REDIS_URL")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
