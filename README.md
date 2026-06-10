# turkdoc

**Understand Turkish government documents in plain English or Arabic.**

turkdoc reads official letters from Turkish institutions — Göç İdaresi, tax offices, municipalities, utilities — and explains what they mean, how urgent they are, what deadlines apply, and what you should do next.

Use it as a **web app** (upload, save, and revisit documents) or from the **terminal** (quick one-off explanations).

> **Disclaimer:** AI-generated explanations for informational purposes only. Not legal advice.

---

## Table of contents

- [Features](#features)
- [Quick start](#quick-start)
- [Web app](#web-app)
- [CLI usage](#cli-usage)
- [Configuration](#configuration)
- [API reference](#api-reference)
- [Deployment](#deployment)
- [Docker](#docker-recommended-for-full-features)
- [Security](#security)
- [Project structure](#project-structure)
- [Example documents](#example-documents)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| | Web app | CLI |
|---|---------|-----|
| Upload photo / PDF | ✓ | ✓ |
| Paste Turkish text | ✓ | ✓ |
| English & Arabic output | ✓ | ✓ |
| Urgency level (LOW / MEDIUM / HIGH) | ✓ | ✓ |
| Deadlines & action steps | ✓ | ✓ |
| Save document history | ✓ | metadata only |
| Re-explain in another language | ✓ | — |

**Powered by:** [Groq](https://groq.com/) (Llama 3.3 70B) · [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) · FastAPI

---

## Quick start

### 1. Prerequisites

- **Python 3.11+**
- **Tesseract OCR** (for photos and PDFs)
  - macOS: `brew install tesseract tesseract-lang`
  - Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-tur`

### 2. Install

```bash
git clone https://github.com/YOUR_USERNAME/resmi-acikla.git
cd resmi-acikla

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e .
cp .env.example .env
```

### 3. Add your Groq API key

Get a free key at [console.groq.com](https://console.groq.com/), then edit `.env`:

```env
GROQ_API_KEY=<paste-your-key-from-console.groq.com>
```

### 4. Run

**Web app:**

```bash
turkdoc-server
```

Open [http://localhost:8000](http://localhost:8000)

**CLI (no server needed):**

```bash
turkdoc demo
```

---

## Web app

1. **Upload** a photo, PDF, or paste Turkish text from a government letter
2. Choose **English** or **Arabic** for the explanation
3. Review the breakdown — urgency, deadlines, next steps, and contacts
4. Documents are **saved automatically** so you can come back later

### What you get per document

- Plain-language **explanation** of what the letter means
- **Urgency** rating with a short reason
- **Deadlines** extracted from the text
- Numbered **action steps**
- **Contacts** (offices, phone numbers, websites when mentioned)
- Option to **re-explain** in the other language

Uploaded files live in `data/uploads/`. Metadata is stored in `data/turkdoc.db`. Both are gitignored and stay on your machine.

Interactive API docs (development only): [http://localhost:8000/docs](http://localhost:8000/docs)

---

## CLI usage

### Explain pasted text

```bash
turkdoc explain --text "Sayın vatandaş, ikamet izniniz..."
```

### Explain a photo or PDF

```bash
turkdoc explain --image letter.jpg
turkdoc explain --image scan.pdf --lang arabic
```

### Run the built-in demo

```bash
turkdoc demo
```

Uses the sample residence permit notice in `examples/residence_permit.txt`.

### View recent history

```bash
turkdoc history
```

Stores only document type, urgency, and timestamp in `~/.turkdoc/history.json` — not the full document text.

### Other commands

```bash
turkdoc explain --text "$(cat examples/tax_notice.txt)" --lang english
turkdoc --version
turkdoc --help
```

### CLI output

The terminal shows color-coded panels:

- Document type and issuing body
- Explanation in your chosen language
- Urgency badge (green / yellow / red) with reason
- Deadlines and numbered action steps
- Disclaimer at the bottom

---

## Configuration

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | **Required.** Groq API key |
| `SECRET_KEY` | placeholder | JWT signing key; **must** be 32+ random chars in production |
| `ENVIRONMENT` | `development` | Set to `production` when deploying |
| `CORS_ORIGINS` | localhost (dev) | Comma-separated allowed origins in production |
| `DATABASE_URL` | `sqlite:///./data/turkdoc.db` | Database connection string |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | JWT lifetime (7 days) |
| `MAX_UPLOAD_SIZE_MB` | `10` | Max file upload size |
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `8000` | Server port |
| `RELOAD` | `true` (dev) | Auto-reload; set `false` in production |

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## API reference

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/documents` | List all documents |
| `GET` | `/api/documents/{id}` | Get document with full explanation |
| `POST` | `/api/documents/upload` | Upload image or PDF (`multipart/form-data`) |
| `POST` | `/api/documents/text` | Submit pasted text (`JSON`) |
| `POST` | `/api/documents/{id}/explain?language=english` | Re-explain in another language |
| `DELETE` | `/api/documents/{id}` | Delete a document |

### Auth (API only — not wired to the web UI yet)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Create account, returns JWT |
| `POST` | `/api/auth/login` | Log in, returns JWT |
| `GET` | `/api/auth/me` | Current user (requires `Authorization: Bearer …`) |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server status |

---

## Deployment

Set environment variables on your host (**never** commit them to git):

```env
ENVIRONMENT=production
GROQ_API_KEY=<your-key>
SECRET_KEY=<random-48-char-string>
RELOAD=false
HOST=0.0.0.0
PORT=8000
```

Optional: `CORS_ORIGINS=https://your-domain.com` if the frontend is served from a different origin.

In production:

- `/docs` and `/redoc` are **disabled**
- Error responses are **sanitized**
- Weak or missing secrets **block startup**

Works on Railway, Render, Fly.io, a VPS with nginx, or any platform that runs Python + Tesseract.

### Docker (recommended for full features)

Docker includes **Tesseract OCR**, **persistent storage**, and **file upload** — everything Vercel cannot do.

**1. Configure `.env`** (copy from `.env.example`):

```env
GROQ_API_KEY=<your-groq-key>
SECRET_KEY=<random-48-char-string>
ENVIRONMENT=production
```

**2. Build and run:**

```bash
docker compose up --build -d
```

Open [http://localhost:8000](http://localhost:8000)

**Other commands:**

```bash
# View logs
docker compose logs -f

# Stop
docker compose down

# Rebuild after code changes
docker compose up --build -d

# Build image only (no compose)
docker build -t turkdoc:latest .
docker run --rm -p 8000:8000 --env-file .env -v turkdoc-data:/app/data turkdoc:latest
```

**Development with hot-reload:**

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Uploads and the database are stored in the Docker volume `turkdoc-data` (production) or `./data` (dev compose).

### Deploy to Vercel

Vercel is supported with limitations (paste-text only, no OCR, ephemeral storage). See **[DEPLOY_VERCEL.md](DEPLOY_VERCEL.md)** for step-by-step setup and required secrets.

See [SECURITY.md](SECURITY.md) for the full production checklist.

---

## Security

| File / folder | Commit to GitHub? |
|---------------|-------------------|
| `.env.example` | ✓ placeholders only |
| `.env` | ✗ never |
| `data/` | ✗ never (uploads + database) |

Before your first push:

```bash
bash scripts/check-secrets.sh
git status   # confirm .env is not listed
```

If an API key was ever exposed, **revoke it** at [console.groq.com](https://console.groq.com/) and create a new one.

---

## Project structure

```
resmi-acikla/
├── backend/           # FastAPI server, database, routes
├── frontend/          # Web UI (HTML, CSS, JS)
├── turkdoc/           # CLI, OCR, Groq explainer
├── docker/            # Docker entrypoint script
├── examples/          # Sample Turkish documents for testing
├── scripts/           # Secret-scanning helper
├── data/              # Local uploads & DB (gitignored)
├── Dockerfile         # Production image
├── docker-compose.yml # Run with Docker Compose
├── .env.example       # Environment template
└── pyproject.toml     # Package & dependencies
```

---

## Example documents

The `examples/` folder has realistic texts for testing without uploading real documents:

| File | Description |
|------|-------------|
| `residence_permit.txt` | Göç İdaresi residence permit renewal notice |
| `tax_notice.txt` | Tax office payment reminder with penalty warning |
| `utility_bill.txt` | İSKİ water bill with late payment warning |

```bash
turkdoc explain --text "$(cat examples/tax_notice.txt)"
```

---

## Limitations

- **Not legal advice** — always verify important matters with a qualified professional
- **OCR quality** — blurry or poorly lit photos may produce incomplete text
- **Turkish focus** — optimized for official bureaucratic Turkish; other languages may be less accurate
- **Internet required** — explanations call the Groq API
- **PDFs** — multi-page scans work, but quality depends on resolution
- **Shared document store** — the web UI does not have per-user login yet; treat local deployments as single-user

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a branch: `git checkout -b feature/my-improvement`
3. Make your changes and test: `turkdoc demo` and/or `turkdoc-server`
4. Run `bash scripts/check-secrets.sh`
5. Open a pull request with a clear description

Ideas: better OCR preprocessing, more output languages, user authentication in the web UI, additional document types.

---

## License

MIT — see [LICENSE](LICENSE).
