# FinWise

## Run Locally

Use Node.js 22.12 or newer for the frontend. This machine already has
Node.js 22.22.2 installed through nvm; select it with `nvm use 22.22.2`
before running the frontend commands.

Start the FastAPI backend from the project root:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a separate terminal, start the Vue frontend:

```sh
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite. The page checks the backend's `/health` endpoint
and displays its connection status. API documentation is available at
http://127.0.0.1:8000/docs.

## Local AI assistant

Install and start Ollama locally, then fetch the model once:

```sh
ollama pull qwen3:8b
ollama serve
```

Keep Ollama bound to the local machine. The backend calls its local HTTP API;
the browser never connects to Ollama. Configure the backend (before starting
FastAPI) with `OLLAMA_MODEL` (default `qwen3:8b`), `OLLAMA_BASE_URL` (default
`http://127.0.0.1:11434`), and `OLLAMA_TIMEOUT_SECONDS` (default `180`).

`POST /api/chat` accepts `message` and an optional `conversation_id`. The
response includes an `assistant_message` and any read-only `tool_results` used
to answer. `DELETE /api/chat/{conversation_id}` clears that conversation.
Conversation history is kept in backend memory, limited to the latest 20
messages and 100 conversations, and resets when the backend restarts.

The system prompt sets the assistant's role and grounding rules. The context
window is the model's finite input for the current inference, so the backend
limits history. Inference is the model producing the next response. When a
question needs account data, the model can request one of six named tools;
FinWise validates the tool and its arguments, runs existing Python finance
services, and returns the computed result for the assistant to explain. The
model does not run SQL or calculate account totals itself.

## API Connection

The frontend API service uses `/api` by default. Vite proxies `/api/*` to
`http://127.0.0.1:8000/*` during development, avoiding cross-origin requests
even when Vite selects a different port.

For production, configure your web server to proxy `/api/*` to FastAPI with
the `/api` prefix removed. Alternatively, set `VITE_API_BASE_URL` to the
backend URL before building and configure FastAPI's allowed CORS origins to
include the deployed frontend's exact origin. Never put secrets in `VITE_*`
variables because they are included in the browser bundle.
