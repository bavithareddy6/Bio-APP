Bioinformatics Web Platform — Blueberry Breeding Program (Django + React + Docker)

Overview
- Full‑stack app for researchers to input up to 10 gene names, fetch their protein sequences, visualize gene expression as an interactive heatmap, and download results.
- Stack: Django (REST API) + PostgreSQL (storage) + React + Plotly (UI) + Docker Compose (runtime).

Key Features
- Upload‑free: bundled data loader ingests provided FASTA + TSV files into Postgres.
- Sequences: Download FASTA for selected genes, choose extension `.fa`/`.fasta`, optional line wrapping.
- Expressions: Interactive Plotly heatmap and TSV export, with missing‑gene reporting.
- Responsive UI: Mobile‑friendly layout, chip‑style gene input, and data table with sticky header.

Data Formats
- FASTA (multi‑line supported):
  - Header: lines start with `>` followed by the gene identifier; the first token after `>` is used as `gene_name`.
  - Sequence: one or more lines of residues; loader concatenates lines.
- TSV (two supported layouts):
  1) 12 columns (no header): 6 repeated [name, value] pairs per row ⇒ gene is column 1; values at columns 2,4,6,8,10,12.
  2) 7 columns (with header): gene name + 6 integer values. Loader auto‑detects layout.
- Zeros are valid expression values (not treated as missing).

Project Structure
- backend/ — Django project and app (API, models, loader, tests)
- frontend/ — React app (Vite dev server, Plotly heatmap, responsive UI)
- data/ — Place your data files here:
  - `data/STRG0A60OAF.protein.sequences.v12.0.fa`
  - `data/all_samples.tsv`

Environment
- Copy the example env and adjust as needed:
  - `cp .env.example .env`
- Defaults:
  - Postgres: user/db/password `bioapp`, host `db`, port `5432`
  - Django: `DEBUG=1`, CORS allows `http://localhost:5173`

Quick Start (Docker Compose)
1) Put your data files into `data/` as listed above.
2) Build and start:
   - `docker compose up --build`
3) Migrate DB and load data (run once):
   - `docker compose exec api python manage.py migrate`
   - `docker compose exec api python manage.py load_bio_data \`
     `--fasta /app/data/STRG0A60OAF.protein.sequences.v12.0.fa \`
     `--tsv /app/data/all_samples.tsv`
4) Open:
   - Frontend: `http://localhost:5173`
   - API health: `http://localhost:8000/api/health`

Using the App
- Enter up to 10 gene names (comma/space separated, or press Enter/comma to add chips).
- Download FASTA: choose extension `.fa`/`.fasta` and optional wrap width.
- View Heatmap: interactive Plotly heatmap + tabular values. Missing genes are listed.
- Download TSV: expression matrix for selected genes.

API Reference
- POST `/_api_/sequences`
  - Body: `{ "genes": ["GeneA", "GeneB"] }`
  - Response: `{ count, not_found: [], sequences: [{ gene, sequence }] }`
- GET `/_api_/sequences/download?genes=GeneA,GeneB[&ext=fa|fasta][&wrap=0|60]`
  - Returns FASTA text (attachment). `ext` controls filename; `wrap` controls line width (0 = single line).
- POST `/_api_/expressions`
  - Body: `{ "genes": ["GeneA", "GeneB"] }`
  - Response: `{ samples: ["Sample1".."Sample6"], rows: [{ gene, values: [6 ints] }], not_found: [] }`
- GET `/_api_/expressions/download?genes=GeneA,GeneB`
  - Returns TSV with header `Gene\tSample1..Sample6`.

Example Requests
- FASTA download (`.fa`, 60‑char wrap):
  - `curl -L -o sequences.fa "http://localhost:8000/api/sequences/download?genes=GeneA,GeneB&ext=fa&wrap=60"`
- Expressions JSON:
  - `curl -X POST http://localhost:8000/api/expressions -H "Content-Type: application/json" -d '{"genes":["GeneA","GeneB"]}'`

Database Schema (Django models)
- `ProteinSequence(gene_name: unique str, sequence: text)`
- `GeneExpression(protein: OneToOne->ProteinSequence, sample1..sample6: int)`

Admin Panel
- Create superuser: `docker compose exec api python manage.py createsuperuser`
- Visit: `http://localhost:8000/admin` (browse ProteinSequence and GeneExpression)

Local Development (optional, without Docker)
- Requirements: Python 3.11, Node 20, Postgres 15
- Backend
  - `cd backend && python -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - Set env vars (`POSTGRES_*`, `DJANGO_*`) and run: `python manage.py migrate && python manage.py runserver`
- Frontend
  - `cd frontend && npm install && npm run dev`

Testing
- Run all tests:
  - `docker compose exec api python manage.py test`
- Run specific tests:
  - `docker compose exec api python manage.py test core.tests.test_api`

Troubleshooting
- Compose warns: “the attribute `version` is obsolete”
  - Harmless. Can be silenced by removing the `version:` key in `docker-compose.yml`.
- Port already in use (8000/5173)
  - Stop conflicting processes or change exposed ports in `docker-compose.yml`.
- Data load mismatch
  - Loader reports created counts. Verify with:
    - `docker compose exec db psql -U bioapp -d bioapp -c "select count(*) from core_proteinsequence;"`
    - `docker compose exec db psql -U bioapp -d bioapp -c "select count(*) from core_geneexpression;"`
- CORS/Network issues
  - Ensure `DJANGO_CORS_ORIGINS` includes the frontend origin (`http://localhost:5173`).

Security & Production Notes
- Turn off DEBUG, set a strong `DJANGO_SECRET_KEY`, and restrict `DJANGO_ALLOWED_HOSTS`.
- Consider serving Django via `gunicorn` and the built frontend via Nginx or a CDN.
- Limit API to authenticated users if deploying beyond local research use.

Roadmap (nice‑to‑have)
- Autocomplete gene names from DB, upload gene list file.
- Heatmap improvements: sorting, color scales, log transform.
- Configurable sample labels instead of `Sample1..Sample6`.
- CI (GitHub Actions) to run tests on push.

Acknowledgements
- Built for a Blueberry breeding program task; uses public libraries: Django, Plotly, React.
