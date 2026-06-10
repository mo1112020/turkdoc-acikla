# Deploy turkdoc to Vercel

## Before you start

Vercel runs turkdoc as a **serverless** app. That means:

| Feature | On Vercel |
|---------|-----------|
| Paste Turkish text | Works |
| Photo / PDF upload | **Not supported** (no Tesseract OCR) |
| Document history | **Temporary** (resets on cold starts unless you add external DB) |
| AI explanations | Works (needs Groq API key) |

For full features (OCR + persistent storage), use [Render](https://render.com) or a VPS instead.

**Timeout:** AI analysis can take 15–30 seconds. Hobby plan allows **10s** max — you may need **Vercel Pro** (60s) for reliable explanations.

---

## 1. Push code to GitHub

Make sure your latest code is on GitHub (including `vercel.json` and `api/index.py`).

---

## 2. Import project on Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. **Import** your repo: `mo1112020/turkdoc-acikla`
3. Framework Preset: **Other**
4. Root Directory: `.` (default)
5. Framework Preset: **FastAPI** (auto-detected) or **Other**
6. Build Command: leave **empty**
7. Output Directory: leave **empty**
8. Install Command: `pip install -r requirements-vercel.txt` (set in `vercel.json`)

> Do **not** add a custom `functions` block in `vercel.json` — Vercel CLI 54+ uses the FastAPI preset via `pyproject.toml` (`tool.vercel.entrypoint`).

Click **Deploy** (it will fail until env vars are set — that's normal).

---

## 3. Environment variables (secrets)

In Vercel: **Project → Settings → Environment Variables**

Add these for **Production** (and Preview if you want):

| Name | Value | Required |
|------|-------|----------|
| `GROQ_API_KEY` | Your key from [console.groq.com](https://console.groq.com/) | **Yes** |
| `SECRET_KEY` | Random 48+ char string (see below) | **Yes** |
| `ENVIRONMENT` | `production` | **Yes** |
| `RELOAD` | `false` | Recommended |

Generate `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Optional variables

| Name | Value | When to use |
|------|-------|-------------|
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Only if frontend is on a different domain |
| `DATABASE_URL` | External Postgres URL | For persistent document storage |
| `MAX_UPLOAD_SIZE_MB` | `10` | Not used on Vercel (uploads disabled) |

**Do not** add `.env` to the repo. Set secrets only in the Vercel dashboard.

---

## 4. Redeploy

After saving environment variables:

**Deployments → … → Redeploy**

---

## 5. Test

Open your Vercel URL, e.g. `https://turkdoc-acikla.vercel.app`

1. Use the **Paste text** tab (not file upload)
2. Paste Turkish text from `examples/tax_notice.txt`
3. Click **Analyze document**

Health check: `https://your-app.vercel.app/health`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `500` on analyze | Check `GROQ_API_KEY` is set; redeploy |
| `504` / timeout | Upgrade to Pro or use shorter text; Groq calls can exceed 10s on Hobby |
| Upload fails | Expected on Vercel — use **Paste text** |
| Documents disappear | Normal on serverless — add `DATABASE_URL` with Postgres/Turso for persistence |
| Build fails | Check Vercel build logs; ensure `requirements.txt` installs |

---

## CLI on Vercel

The `turkdoc` CLI is for local use only. Vercel deploys the **web app + API**.
