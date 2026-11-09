from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FinWise API",
    description="AI-powered Personal Finance Assistant",
    version="0.1.0"
)

# Allow the Vue frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to FinWise",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }