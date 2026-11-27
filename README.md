# Space-Based Infrastructure Intelligence Platform

A backend platform for satellite-based infrastructure monitoring. It provides APIs for registering satellite images, managing monitoring areas and infrastructure assets, and storing and querying detected changes.

## 1. Main Technologies

- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- PostGIS
- GeoAlchemy2
- GeoPandas, Rasterio, Shapely and PyProj
- Alembic
- Pytest

## 2. Project Structure

```text
.
├── app/
│   ├── api/          # API endpoints
│   ├── db/           # Database configuration and spatial utilities
│   ├── models/       # Database models
│   ├── schemas/      # Request and response schemas
│   └── main.py       # FastAPI application
├── docs/
│   └── API.md        # API reference
├── migrations/
│   ├── env.py
│   └── versions/     # Alembic migration scripts
├── test/             # Automated tests
├── .env              # Local database configuration (not committed)
├── requirements.txt
├── alembic.ini
└── README.md
```

## 3. Requirements

Install the following before setting up the project:

- Python 3.13
- Git
- PostgreSQL with the PostGIS extension (for the PostgreSQL setup)

## 4. Installation

Clone the repository:

```bash
git clone <repository-url>
cd Space-Based-Infrastructure-Intelligence-Platform
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## 5. Database Configuration

The application supports PostgreSQL/PostGIS and SQLite.

### PostgreSQL with PostGIS

Create a `.env` file in the project root:

```env
DB_USER=space_user
DB_PASSWORD=your_local_database_password
DB_HOST=127.0.0.1
DB_PORT=5433
DB_NAME=space_infra
```

Replace the password with your own local database password. Do not commit `.env` to GitHub.

The application uses these variables to construct its PostgreSQL connection.

Make sure PostgreSQL is running and the PostGIS extension is available in the database.

### SQLite fallback

If `DB_PASSWORD` is not set, the application uses `DATABASE_URL` if provided. Otherwise, it uses:

```text
sqlite:///./space_infra_dev.sqlite3
```

SQLite is also used by the automated tests through isolated test databases.

## 6. Database Migrations

The project uses Alembic. Migration scripts are stored in `migrations/versions/`.

To apply all migrations:

```bash
python -m alembic upgrade head
```

To check the current migration revision:

```bash
python -m alembic current
```

To list available migration heads:

```bash
python -m alembic heads
```

Run migrations after configuring the database you intend to use.

## 7. Running the API

Start the development server:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Useful endpoints:

| Endpoint | Purpose |
|---|---|
| `/` | Basic application information |
| `/health` | Health check |
| `/docs` | Interactive Swagger API documentation |
| `/openapi.json` | OpenAPI specification |

## 8. API Modules

The backend currently provides:

- **Monitoring Areas:** Create and retrieve monitoring areas.
- **Infrastructure Assets:** Register and retrieve assets, with spatial validation and filtering.
- **Satellite Images:** Register and retrieve satellite image metadata.
- **Detections:** Create and retrieve detections, filter detection records, and find detections near infrastructure assets.

For endpoint details, request examples, query parameters, and validation rules, see:

[API Reference](docs/API.md)

## 9. Running Tests

Run the automated test suite:

```bash
python -m pytest -q
```

The tests use isolated SQLite databases, so they do not require the local PostgreSQL database to run.

## 10. Spatial Data Conventions

- The backend uses **EPSG:4326** as its geometry storage CRS.
- GeoJSON coordinates follow the longitude, latitude order.
- Incoming geometries are transformed to the storage CRS when necessary.
- PostgreSQL uses PostGIS spatial operations for supported spatial queries.

## 11. Git Collaboration

Create a feature branch for your work:

```bash
git checkout -b feature/your-feature-name
```

After making changes:

```bash
git add .
git commit -m "Describe your changes"
git push -u origin feature/your-feature-name
```

Submit a Pull Request to merge your feature branch into `main`. Avoid committing `.env`, virtual environments, database files, or Python cache files.