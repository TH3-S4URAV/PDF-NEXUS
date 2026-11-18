# PDF NEXUS — Production Deployment Guide

## 1. Hosting Architecture Recommendation

| Component | Recommended Host | Alternatives |
|---|---|---|
| **Frontend** | Vercel / Netlify | Cloudflare Pages, AWS S3 + CloudFront |
| **Backend API** | Render / Railway / Fly.io | AWS ECS, Google Cloud Run |
| **Database** | Supabase PostgreSQL / Neon | AWS RDS, Local SQLite with persistent volume |
| **Object Storage**| AWS S3 / Cloudflare R2 | Local persistent volumes |

---

## 2. Docker Production Deployment
Run both frontend (Nginx) and backend (FastAPI + PyMuPDF) using Docker Compose:

```bash
docker-compose up -d --build
```

Nginx serves the built React application and automatically reverse-proxies `/api/` traffic to the backend container.

---

## 3. Deploying Frontend to Vercel / Netlify

1. **Build Command**: `npm run build`
2. **Output Directory**: `dist`
3. **Environment Variable**: `VITE_API_BASE_URL=https://your-backend-api.onrender.com/api`

---

## 4. Deploying Backend to Render / Railway

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `python run.py`
3. **Environment Variables**:
   - `SECRET_KEY`: Set to a 64-character random string.
   - `DATABASE_URL`: Your PostgreSQL connection string.
   - `CORS_ORIGINS`: Your live frontend domain (e.g. `https://pdf-nexus.vercel.app`).
