# project/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from openai import AsyncOpenAI

from app.routes.analyze_ip import router as analyze_ip_router
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern startup handler replacing deprecated @app.on_event.
    """

    # -------- Startup: Check LLM Connection --------
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    test_model = "gpt-4.1-mini"

    try:
        resp = await client.chat.completions.create(
            model=test_model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1
        )
        print(f"[STARTUP] LLM connectivity OK → {test_model}")

    except Exception as e:
        print(f"[STARTUP ERROR] Failed to reach LLM: {e}")
        raise RuntimeError("LLM model connection failed. Server will not start.")

    yield  # -------- Application Running --------

    # -------- Shutdown (Optional) --------
    print("[SHUTDOWN] Server closing...")


# Create app with lifespan manager
app = FastAPI(
    title="IP Threat Intelligence API",
    version="1.0.0",
    lifespan=lifespan
)


# CORS MIDDLEWARE

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OR specify: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routes
app.include_router(analyze_ip_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
