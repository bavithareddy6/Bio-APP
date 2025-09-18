Bioinformatics Web Platform (Django + React + Docker)

Overview
- Full-stack app to fetch protein sequences from a FASTA file, visualize gene expression as an interactive heatmap, and download results.
- Stack: Django (API) + PostgreSQL (DB) + React + Plotly (Frontend) + Docker Compose.

Data Assumptions
- FASTA: Multi-line sequence entries, headers like `>GeneName ...`. First token after `>` is the gene identifier.
- TSV: 12 columns per row representing 6 repeated pairs: [gene_name, value] × 6. Zeros are valid expression values (not missing). If you provide a 7-column TSV (gene + 6 values), the loader will detect and parse it as well.

Project Structure
- backend/ — Django project and app (API, models, loader)
- frontend/ — React app (Plotly heatmap, downloads)
- data/ — Place your data files here:
  - data/STRG0A60OAF.protein.sequences.v12.0.fa
  - data/all_samples.tsv

Quick Start (Docker)
1) Create a `.env` file from example and adjust if needed:
   cp .env.example .env

2) Put data files into `data/` as noted above.

3) Build and start services:
   docker compose up --build

4) Initialize database and load data (run once):
   docker compose exec api python manage.py migrate
   docker compose exec api python manage.py load_bio_data \
     --fasta /app/data/STRG0A60OAF.protein.sequences.v12.0.fa \
     --tsv /app/data/all_samples.tsv

5) Open the app:
   Frontend: http://localhost:5173
   API: http://localhost:8000/api/

API Endpoints
- POST /api/sequences — Body: {"genes":["GeneA","GeneB"]} → JSON sequences
- GET  /api/sequences/download?genes=GeneA,GeneB[&ext=fa|fasta][&wrap=0|60] → FASTA download (text/plain).
  - `ext`: default `fasta`; set `fa` to download with `.fa` extension.
  - `wrap`: default `0` (single line per sequence). Set to `60` (or any positive integer) to wrap sequence lines.
- POST /api/expressions — Body: {"genes":["GeneA","GeneB"]} → JSON matrix for heatmap
- GET  /api/expressions/download?genes=GeneA,GeneB → TSV download

Notes
- Zero values are stored and treated as valid.
- If some genes are missing in either dataset, APIs return partial results with a `not_found` list.
- CORS is enabled for local development.

FASTA Format Notes
- Each sequence must start with a header line beginning with `>` followed by the gene identifier (e.g., `>GeneX`).
- Sequence lines contain only residue characters; whitespace is not required and wrapping is optional. Single-line or fixed width (e.g., 60 chars) are both valid.
- File extension `.fa` or `.fasta` does not matter to most tools; content matters.
