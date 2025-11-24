import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # External API Keys
    ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_API_KEY")
    IPQS_KEY = os.getenv("IPQUALITYSCORE_API_KEY")
    IPAPI_KEY = os.getenv("IPAPI_API_KEY")
    VIRUSTOTAL_KEY = os.getenv("VIRUSTOTAL_API_KEY")

    # LLM Provider
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Cache + Redis
    CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 86400))
    CACHE_VERSION = os.getenv("CACHE_VERSION", "v1") 

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    def validate(self):
        missing = []
        if not self.ABUSEIPDB_KEY:
            missing.append("ABUSEIPDB_API_KEY")
        if not self.IPQS_KEY:
            missing.append("IPQUALITYSCORE_API_KEY")
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")

        if missing:
            raise RuntimeError(f"Missing required environment variables: {missing}")

settings = Settings()
