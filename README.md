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

## Document Intelligence (Milestone 4)

Document Intelligence accepts PDFs up to 20 MB. Files are written under
`backend/storage/documents` with random server-generated names; the API returns
the original display name and metadata, never the storage path. Uploaded files
remain on the local machine. Authentication is not part of this single-user
app yet, so add per-user ownership checks before exposing this feature to
multiple accounts.

Fetch the embedding model as well as the chat model:

```sh
ollama pull nomic-embed-text
ollama pull qwen3:8b
```

Use **Documents** in the app to upload and process a text PDF. The upload is
stored as `PENDING`; processing extracts selectable text and records
page-numbered chunks and embeddings in SQLite. A scanned PDF with no selectable
text is marked `FAILED` with an explicit message that OCR is not implemented.
`OLLAMA_EMBED_MODEL` can override the default embedding model. The upload limit
can be changed with `DOCUMENT_MAX_UPLOAD_BYTES`.

The document API is `POST /api/documents/upload` (multipart field `file`),
`GET /api/documents`, `GET /api/documents/{id}`,
`DELETE /api/documents/{id}`, `POST /api/documents/{id}/process`, and
`POST /api/documents/ask` with `{ "question": "..." }`. Answers include source
document names and page references.

### RAG in plain language

- **Embeddings** are number lists that capture a passage's meaning. Similar
  passages tend to have number lists pointing in similar directions.
- **Chunking** cuts a long document into smaller overlapping passages. This
  gives retrieval focused evidence while overlap helps keep a sentence that
  crosses a cut intact.
- **Vector similarity** compares the question's embedding with each passage's
  embedding. FinWise ranks them by cosine similarity and sends the closest five
  passages to the language model.
- **Retrieval-Augmented Generation (RAG)** means finding evidence first, then
  asking the model to answer from that evidence. The prompt treats PDF contents
  as untrusted data, asks the model to admit when facts are missing, and the
  response carries source excerpts and page numbers.

For local simplicity, embeddings are stored as JSON in SQLite and ranked in
Python. That is appropriate for a small personal collection, but a full scan is
linear in the number of chunks. The production migration is to PostgreSQL:
install pgvector, add a `vector(768)` column (confirm the active embedding
model's dimension), migrate the JSON vectors, and use pgvector cosine-distance
ordering with an HNSW or IVFFlat index as the collection grows. Keep document
metadata and ownership in relational tables; retrieval must filter by owner
once authentication is added. Re-embed all chunks if changing embedding models.

## API Connection

The frontend API service uses `/api` by default. Vite proxies `/api/*` to
`http://127.0.0.1:8000/*` during development, avoiding cross-origin requests
even when Vite selects a different port.

For production, configure your web server to proxy `/api/*` to FastAPI with
the `/api` prefix removed. Alternatively, set `VITE_API_BASE_URL` to the
backend URL before building and configure FastAPI's allowed CORS origins to
include the deployed frontend's exact origin. Never put secrets in `VITE_*`
variables because they are included in the browser bundle.
