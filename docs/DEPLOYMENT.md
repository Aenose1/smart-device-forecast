# Deploying Smart Device Forecast to Vercel

You can deploy **both the frontend and the backend directly on Vercel** in a single project with zero external dependencies, making it super easy to show and demo your project!

---

## Option 1: Full-Stack Vercel Deployment (Frontend + Backend on Vercel) — RECOMMENDED

With this setup, Vercel hosts:
- **Frontend**: The React (Vite + Tailwind) single-page app on Vercel's global CDN.
- **Backend**: The FastAPI backend running as a Serverless Python function (`api/index.py`).
- **Database**: The 209-device catalogue + 6,339 price history records pre-seeded in SQLite, automatically loaded on startup!

### Steps:
1. Push your repository to GitHub:
   ```powershell
   git add -A
   git commit -m "Add expanded dataset, Vercel serverless backend, and run scripts"
   git push origin main
   ```
2. Log in to [Vercel](https://vercel.com/) and click **"Add New..." -> "Project"**.
3. Import your GitHub repository.
4. Keep the **Root Directory** as `./` (the repository root — do NOT select `frontend`).
5. Vercel will automatically read `vercel.json` and `package.json`:
   - **Build Command**: `npm run build` (automatically runs `npm --prefix frontend install && npm --prefix frontend run build`)
   - **Output Directory**: `frontend/dist`
   - **Serverless API**: `api/index.py` handles all `/api/*` routes.
6. Click **Deploy**!

Once deployed, your live URL (e.g., `https://your-project.vercel.app`) has both the frontend and backend running with zero extra configuration.

---

## Option 2: Running Locally on Windows

You have two options to run locally:

### 1-Click Launch (Easiest):
Simply double-click `run.bat` in the project root folder. It will:
- Activate (or create) the Python `.venv`
- Start the FastAPI backend on `http://127.0.0.1:8000`
- Start the React frontend on `http://localhost:5173`

### Manual Launch (Two Terminals):

**Terminal 1 — Backend (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000
```
- Health check: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Interactive API Docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

**Terminal 2 — Frontend (PowerShell):**
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open [http://localhost:5173](http://localhost:5173).

---

## Option 3: Separate Frontend (Vercel) + External Backend (Render / Cloud)

If you prefer hosting the backend on Render or an external VPS with PostgreSQL:
1. Deploy the backend to Render with `DATABASE_URL` pointing to PostgreSQL.
2. In Vercel Project Settings for the frontend, add the Environment Variable:
   - `VITE_API_URL`: `https://your-backend-app.onrender.com` (no trailing slash).
3. Redeploy the frontend in Vercel.

---

## Verification Checklist

- [x] **Catalogue**: 209 devices across 21 top brands (Apple, Samsung, Google, OnePlus, Xiaomi, Redmi, Vivo, OPPO, Realme, Motorola, POCO, Nothing, Dell, Lenovo, HP, ASUS, Acer, MSI, Microsoft, Gigabyte, Razer).
- [x] **Price History**: 6,339 historical monthly price points spanning up to 3 years.
- [x] **Vercel Serverless Function**: `api/index.py` configured with automatic `/tmp` database and model directory handling.
- [x] **Root Vercel Config**: `vercel.json` maps static assets to `frontend/dist` and `/api/*` to `api/index.py`.
- [x] **Automated Tests**: 55/55 pytest tests passing.
