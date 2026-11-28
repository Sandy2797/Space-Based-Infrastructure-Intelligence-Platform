# Space-Based Infrastructure Intelligence Platform

Backend platform for satellite-based infrastructure monitoring. It provides versioned APIs for monitoring areas, infrastructure assets, satellite image metadata, and detected changes.

## Technology

- Python 3.13, FastAPI, Pydantic
- SQLAlchemy, Alembic, PostgreSQL/PostGIS
- SQLite for isolated tests
- Rasterio, Shapely, PyProj, GeoAlchemy2
- Pytest

## Repository layout

```text
app/
  api/          FastAPI routers
  db/           database sessions and spatial storage helpers
  models/       SQLAlchemy models
  schemas/      Pydantic request/response schemas
  services/     raster metadata and image-registration services
migrations/     Alembic environment and versioned migrations
test/           automated tests
docs/           API, data dictionary, decisions, architecture and GIS docs
```

## Setup (Windows PowerShell)

```powershell
git clone https://github.com/Sandy2797/Space-Based-Infrastructure-Intelligence-Platform.git
cd Space-Based-Infrastructure-Intelligence-Platform
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Database configuration

The backend supports PostgreSQL/PostGIS and SQLite. For PostgreSQL, create a local `.env` file in the repository root:

```env
DB_USER=space_user
DB_PASSWORD=replace_with_your_local_password
DB_HOST=127.0.0.1
DB_PORT=5433
DB_NAME=space_infra
```

Use your own local credentials. Never commit `.env`. Ensure the PostgreSQL server is running and PostGIS is installed in the target database.

Without `DB_PASSWORD`, the application uses `DATABASE_URL` when set; otherwise it falls back to `sqlite:///./space_infra_dev.sqlite3`.

## Migrations

Apply migrations to the configured database:

```powershell
python -m alembic upgrade head
python -m alembic current
python -m alembic heads
```

The current migration chain is the source of truth; do not use `Base.metadata.create_all()` as a replacement for production migrations.

## Run the API

```powershell
python -m uvicorn app.main:app --reload
```

Open:
- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI: http://127.0.0.1:8000/openapi.json
- Health: http://127.0.0.1:8000/health

## Run tests

```powershell
python -m pytest -q
```

The reported local baseline before this update was 67 passing tests. Run the suite again after pulling changes and report the actual result from your machine.

## Current APIs

- `/api/v1/monitoring-areas`
- `/api/v1/infrastructure-assets`
- `/api/v1/images`
- `/api/v1/detections`

See [API reference](docs/API.md) for payloads, validation, filters and limitations. See [Detection integration contract](docs/contracts/detection-v1.md) for the current backend schema snapshot.

## GIS conventions

- Geometry storage and API output: EPSG:4326.
- GeoJSON coordinate order: longitude, latitude.
- PostgreSQL uses PostGIS geometry; SQLite uses JSON geometry.
- Raster registration currently extracts metadata from a locally accessible raster. The image API registers metadata and a file reference; it does not upload or provide production object storage.

## Data handling and safety

Do not commit `.env`, credentials, local database files, private datasets, raster files, model checkpoints, or generated outputs. Keep approved imagery and AI datasets in their designated local/approved storage locations. Preserve original imagery and evidence references.

A missing permit record is not proof of illegal activity. Model predictions and verification recommendations require human review.

## Git workflow

```powershell
git switch -c feature/your-task
git add <specific-files>
git commit -m "Describe the change"
git push -u origin feature/your-task
```

Open a pull request to `main`, request review, and wait for required checks. Avoid force-pushing shared branches. Keep each teammate's implementation on their own feature branch and integrate through reviewed contracts and pull requests.

## Integration dependencies

- AI detection and evidence semantics: Nada
- NBVE request/response and verification-case behavior: Rana
- Authentication and authorization: Seif
- Feedback and audit events: Mohamed
- Backend APIs, GIS validation, persistence, migrations and integration support: Sandy

Do not invent or silently alter another component's contract. Update the contract documents when the responsible owner confirms a change.
