# Smart Device Price Prediction & 3-Year Forecasting System

Full-stack app that shows historical prices for laptops and smartphones and produces **estimated** future prices
(1-5 years, default 3). Stack: React + TypeScript + Tailwind, FastAPI, SQLAlchemy (SQLite for local use, PostgreSQL for
Docker/production), scikit-learn / statsmodels, reportlab (PDF).

> Forecasts are estimates based on historical price patterns and may differ from actual market prices.
> The data in `data/sample` is **synthetic demo data**, labelled as such everywhere. Use real CSVs for real forecasts.

---------------------------------------------------------------------------------------------------------

## Run it on Windows (PowerShell + VS Code)

You need: **Python 3.10-3.13** (tick "Add python.exe to PATH" in the installer) and **Node.js 18+** (nodejs.org, LTS).
Check with `python --version` and `node --version`.

### Step 1. Extract and open the RIGHT folder

Extract `the project ZIP` (right-click -> Extract All). In VS Code choose **File -> Open Folder** and select
the folder that **directly contains** `requirements.txt`, `README.md`, `backend`, `frontend` and `ml`.
Then open a terminal: **Terminal -> New Terminal** (PowerShell).

Check you are in the right place. This must print `True`:

```powershell
Test-Path requirements.txt
```

If it prints `False` (or you see "Could not open requirements file ... 'requirements.txt'"), you are one folder too high or
too low. Run `dir` and `cd` into the folder that contains `requirements.txt`.

### Step 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell says *"running scripts is disabled on this system"*, allow scripts **for this terminal window only**, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of the prompt. When VS Code asks to use the new environment, click **Yes**
(or Ctrl+Shift+P -> "Python: Select Interpreter" -> the one in `.venv`).

### Step 3. Install the Python packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Open `.env` and make sure these lines are set (do not put spaces around `=`). The defaults are already right for a local run;
the only one you must add yourself is the administrator key if you want to use the Administration pages:

```
DATABASE_URL=sqlite:///./dev.db
SEED_SAMPLE_DATA=true
ADMIN_API_KEY=type-any-long-text-of-at-least-16-characters
```

There is **no login**: you do not need an account to use the site. `ADMIN_API_KEY` only protects the Administration pages
(datasets, models, device editing); leave it empty to turn those pages off. For a local classroom demo you can instead set
`ALLOW_OPEN_ADMIN=true` (no key; ignored on any production server).
`DATABASE_URL=sqlite:///./dev.db` is a local file database (nothing to install). `SEED_SAMPLE_DATA=true` loads the demo catalogue.

### Step 5. Initialise the database

```powershell
python -m scripts.seed --sample
```

This creates the tables and loads the sample catalogue and its price history (the price histories are synthetic demo data,
labelled as such in the app). It is safe to repeat. The backend also does this itself on start-up when `SEED_SAMPLE_DATA=true`.

### Step 6. Start the backend (leave this terminal open)

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

- Health check: http://localhost:8000/api/health  (should show `{"status":"ok"}`)
- API documentation (Swagger): http://localhost:8000/api/docs

### Step 7. Start the frontend (second terminal)

Click the **+** in the terminal panel to open a new PowerShell, then:

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The dev server forwards `/api` requests to the backend on port 8000, so the backend must be running.

### Step 8. Use the site

Open **http://localhost:5173**. Nothing to sign in to: the home page, catalogue, comparison, forecasts, dashboard and your
forecast history are available immediately. Your forecast history is remembered per browser (an anonymous random id in
`localStorage`; clearing site data starts a new, empty history). The gear icon in the top bar opens **Administration**, which asks for
`ADMIN_API_KEY`. API documentation: **http://localhost:8000/api/docs**.

### Updating an EXISTING database to the new catalogue (safe, repeatable)

```powershell
python -m scripts.seed --sync-catalog          # adds missing devices / price rows, never deletes users or forecasts
python -m scripts.seed --retire-legacy-demo    # optional: removes the old fictional demo devices
```

### Run the tests (optional)

With the virtual environment active, from the project root:

```powershell
pytest -q
```

Tests use a temporary database and do not touch `dev.db`.

---------------------------------------------------------------------------------------------------------

## Deploying to Vercel + Render

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for the exact environment variables, the database-persistence requirement on Render,
the Git commands, and the post-deploy checklist. Short version: on Vercel set `VITE_API_URL=https://smart-device-forcast-1.onrender.com`;
on Render set a PostgreSQL `DATABASE_URL`, `TRUST_PROXY=true` and (optionally) `ADMIN_API_KEY`.

## Images and design

* All pictures are **original illustrations stored locally** in `frontend/public/images/` (generated by
  `scripts/generate_images.py`; regenerate with `python -m scripts.generate_images`). They are *not* photographs of the real
  products and no manufacturer logos are used; the UI says so. Nothing is hot-linked.
* `ProductImage` shows a skeleton while loading, falls back to the illustration if a photo fails, then to an icon.
* To use a licensed product photo for one device, add a spec `Image URL` in Admin (a `/images/...` path inside
  `frontend/public/images/` or an `https://` URL you have rights to). Failed photos fall back automatically.
* Icons are Lucide-style SVG paths (ISC licence) inlined in `components/Icon.tsx` (no extra dependency).
* Catalogue prices are approximate reference launch prices; the price **histories are synthetic demo data** and are labelled so.

## Troubleshooting

| Message | Cause and fix |
|---|---|
| `Could not open requirements file ... requirements.txt` | Wrong folder. `cd` into the folder that contains `requirements.txt` (Step 1). |
| `running scripts is disabled` | Use the `Set-ExecutionPolicy -Scope Process ...` command in Step 2. |
| `ModuleNotFoundError: No module named 'backend'` | Run uvicorn/seed/pytest from the project root, not from `frontend`. |
| `ValidationError ... database_url Field required` | `.env` is missing or misnamed (it must be called `.env`, in the project root). |
| `connection refused` on port 5432 | `.env` still has the PostgreSQL URL; use `sqlite:///./dev.db` for local runs. |
| Frontend loads but shows "Cannot reach the server" | Backend (Step 6) is not running. |
| No devices in the list | `SEED_SAMPLE_DATA=true` was not set; delete `dev.db`, set it, run Step 5 again. |
| `pip` tries to compile packages / fails to build | Use Python 3.10-3.13 64-bit; avoid pre-release Python versions. |
| `uvicorn is not recognized` | The virtual environment is not active (Step 2), or packages are not installed (Step 3). |

## Docker (PostgreSQL) alternative
```bash
cp .env.example .env            # set POSTGRES_PASSWORD and ADMIN_API_KEY; use the PostgreSQL DATABASE_URL line
docker compose up --build       # then open http://localhost:8000
```
Docker was not run while preparing this package; see `docs/ARCHITECTURE.md` and the notes at the end of this file.

## Data workflow
1. Admin -> **Overview & devices**: add devices (ID like `LP001`, specs as `RAM=16 GB`, one per line).
2. Admin -> **Datasets**: upload CSV (`device_id,device_name,category,date,price,source,currency`, dates `YYYY-MM-DD`).
   "Validate only" is a dry run. Valid rows are stored; missing values, bad dates/prices, unknown IDs, name/category/currency
   mismatches and duplicates are reported per row. A template is in `data/price_history_template.csv`.
3. Users pick a device -> **Generate forecast** -> CSV (`device_3_year_forecast.csv`) and PDF downloads.
4. Admin -> **Models & logs**: retrain and inspect metrics. Models also retrain automatically when a device's data changes.

A device needs at least 8 distinct price dates spanning at least 90 days to be forecast.

## Project layout
`frontend/` React app - `backend/app` FastAPI (routers, services) - `ml/` forecasting pipelines (separate laptop and
smartphone pipelines) - `data/` sample + uploads - `models/` trained artifacts - `scripts/` seed / sample / schema tools -
`database/schema.sql` PostgreSQL DDL - `docs/` notes.

## Security notes
No user accounts, passwords or cookies. Visitors are anonymous; each browser's forecast history is separated by a random id
(not a credential, so keep forecasts you consider sensitive out of the public deployment). Administration (`/api/admin/*`: dataset upload,
model training, device create/edit/delete, logs, export) requires the `X-Admin-Key` header matching `ADMIN_API_KEY`
(constant-time comparison), is disabled when the key is unset, and the demo "open admin" switch is ignored in production.
CORS allows only the listed origins, methods and headers. Request validation, parameterised SQL, CSV-only uploads with a size cap,
formula-injection-safe CSV exports, per-IP rate limits on forecasting, secrets only from environment variables (nothing secret is
ever in a `VITE_` variable or the frontend). Before production: PostgreSQL, a strong `ADMIN_API_KEY`, `ENVIRONMENT=production`,
`TRUST_PROXY=true`, database backups.

## API summary
Public: `GET /api/health`, `/api/public/overview`, `/api/devices[/search|/brands|/facets|/{id}|/{id}/history[?format=csv]]`,
`POST /api/forecast`, `POST /api/predict`, `GET /api/predictions[/{id}[/csv|/pdf]]` (this browser's history), `GET /api/dashboard`.
Administration (needs `X-Admin-Key`): `GET /api/admin/status` (open), `POST|PUT|DELETE /api/admin/devices[/{id}]`,
`POST /api/admin/dataset/{upload,validate}`, `GET /api/admin/{datasets,dataset/export,models,prediction-logs,overview}`,
`POST /api/admin/models/train`. Browsers send an anonymous `X-Visitor-Id` header.

## Verification status of this package
Prepared in a sandbox whose package registries (PyPI, npm) were blocked by network policy, so the following were **NOT run**:
`pip install`, the backend test-suite (including the new auth tests), the real FastAPI server, `npm install`, `tsc`,
`vite build`, and the real Recharts charts. What *was* run: Python syntax checks of all backend files; the new password
validator in isolation; an esbuild bundle of the whole frontend source; and a Chromium browser test of the real React
source against a **mock** API built from your catalogue CSV (register, login, logout, protected redirect, catalogue brand
filters incl. Acer Aspire/Swift/Nitro/Predator Helios/TravelMate, search, price filter, sorting, device page, forecast
display, image loading and fallback, no horizontal overflow at 1440/820/390 px). The mock's forecast numbers are not from the ML pipeline.
Please run `pip install -r requirements.txt && pytest -q` and `cd frontend && npm install && npm run build` once on your machine;
fix anything those report before pushing.
