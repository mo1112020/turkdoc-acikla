# Deploy turkdoc to Railway

Railway runs the full app via Docker — including **Tesseract OCR**, **photo/PDF upload**, and **persistent storage** (with a volume).

---

## 1. Push code to GitHub

Make sure your latest code is on GitHub.

---

## 2. Create a Railway project

1. Go to [railway.com](https://railway.com) and sign in
2. **New Project** → **Deploy from GitHub repo**
3. Select `mo1112020/turkdoc-acikla`
4. Railway detects `railway.toml` and builds from the **Dockerfile**

---

## 3. Environment variables

In Railway: **Project → your service → Variables**

| Variable | Value | Required |
|----------|-------|----------|
| `GROQ_API_KEY` | Your key from [console.groq.com](https://console.groq.com/) | **Yes** |
| `SECRET_KEY` | Random 48+ char string (see below) | **Yes** |
| `ENVIRONMENT` | `production` | **Yes** |
| `RELOAD` | `false` | Recommended |
| `HOST` | `0.0.0.0` | Recommended |

> **Healthcheck failed?** The app starts even with missing vars, but analysis will not work until **both** `GROQ_API_KEY` and `SECRET_KEY` are set. Check **Deploy logs** for `Startup warning`.

Generate `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Railway sets `PORT` automatically — do not override it.

Optional:

| Variable | When to use |
|----------|-------------|
| `CORS_ORIGINS` | `https://your-app.up.railway.app` if needed |
| `DATABASE_URL` | External Postgres instead of SQLite |

**Never** commit `.env` to GitHub.

---

## 4. Persistent storage (recommended)

Without a volume, uploads and the database are lost on redeploy.

1. **Service → Settings → Volumes**
2. **Add Volume** → mount path: `/app/data`
3. Redeploy

---

## 5. Public URL

1. **Service → Settings → Networking**
2. **Generate Domain**
3. Open `https://your-app.up.railway.app`

Health check: `https://your-app.up.railway.app/health`

---

## 6. Test

1. Upload a photo/PDF **or** paste Turkish text
2. Choose English or Arabic
3. Click **Analyze document**

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Build fails | Check **Deployments → Build logs** |
| `500` on analyze | Verify `GROQ_API_KEY` and `SECRET_KEY` are set |
| Healthcheck failure | Set `GROQ_API_KEY`, `SECRET_KEY` (32+ chars), `ENVIRONMENT=production`; check Deploy logs |
| `ready: false` on `/health` | Add missing vars from the `missing` list in the health response |
| Documents lost after redeploy | Add volume at `/app/data` |
| OCR fails | Dockerfile includes Tesseract — rebuild the image |

---

## Local Docker (same image as Railway)

```bash
docker compose up --build -d
```

Open [http://localhost:8000](http://localhost:8000)
