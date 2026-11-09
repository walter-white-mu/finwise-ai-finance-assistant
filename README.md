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

## API Connection

The frontend API service uses `/api` by default. Vite proxies `/api/*` to
`http://127.0.0.1:8000/*` during development, avoiding cross-origin requests
even when Vite selects a different port.

For production, configure your web server to proxy `/api/*` to FastAPI with
the `/api` prefix removed. Alternatively, set `VITE_API_BASE_URL` to the
backend URL before building and configure FastAPI's allowed CORS origins to
include the deployed frontend's exact origin. Never put secrets in `VITE_*`
variables because they are included in the browser bundle.
