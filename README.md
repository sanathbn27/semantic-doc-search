# Semantic Document Search

A small REST API for storing short text documents and searching them by
**semantic similarity** rather than exact keyword matching. A query like
"thruster firing sequence" will correctly surface a document about
propulsion even if it doesn't contain those exact words.

## How it works

1. When a document is created (`POST /documents`), its `content` is
   converted into a 384-dimensional vector using a pretrained sentence
   embedding model (`all-MiniLM-L6-v2`). The vector is stored alongside
   the document.
2. When searching (`GET /documents/search`), the query string is
   converted into a vector the same way, then compared against every
   stored document's vector using cosine similarity. Results are
   returned ranked by similarity score, most relevant first.

No vector database is used, similarity is computed directly with numpy,
which is sufficient at this scale (a handful of documents).

## Tech stack

- **FastAPI** — web framework
- **SQLite** — persistence (single file, no setup)
- **SQLAlchemy** — ORM
- **Pydantic v2** — request/response validation
- **sentence-transformers** (`all-MiniLM-L6-v2`) — embeddings, runs
  locally, no API key required

## Getting the code

```bash
git clone https://github.com/sanathbn27/semantic-doc-search.git
cd semantic-doc-search
```

## Setup

Requires Python 3.11+. (Python 3.9 will fail to install one dependency
on Windows without a C++ compiler — use 3.11 or newer.)

```bash
py -3.11 -m venv .venv          # Windows — use py launcher to force 3.11
python3.11 -m venv .venv         # macOS/Linux equivalent, if multiple versions installed

source .venv/bin/activate        # macOS/Linux
.venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -r requirements.txt
```

**Note:** plain `python -m venv` may pick up an older Python version if multiple are installed (e.g. Python 3.9 via Anaconda). If `pip install` fails with a build error mentioning `greenlet` or a missing C++ compiler, this is almost always the cause — recreate the venv forcing Python 3.11 specifically as shown above.

The first run downloads the embedding model (~90MB) from Hugging Face.
This requires an internet connection once; it's cached locally after
that.



## Run

```bash
uvicorn app.main:app --reload
```

The API is now running at `http://127.0.0.1:8000`. Interactive docs
(Swagger UI) are available at `http://127.0.0.1:8000/docs`, every
endpoint below can be tried directly from there.

## API

### Seeding sample data

A helper script if needed, `seed.py`, posts the 5 sample documents from the spec
to a running instance of the API:

```bash
python seed.py
```

**Note:** this script always creates new documents, it doesn't check
whether they already exist. Running it more than once against the same
database will create duplicate entries, which will appear redundantly
in search results. Use it once against a fresh `documents.db`, or
delete `documents.db` before re-running it.

### `POST /documents`

Store a new document. Computes and stores its embedding.

```json
{
  "title": "RCS Thruster Firing Procedure",
  "content": "This procedure describes the cold gas thruster ignition sequence..."
}
```

Returns the stored document (`201 Created`) with its generated `id` and
`created_at`. The internal embedding is never exposed in API responses.



### `GET /documents/search?q=<query>&top_k=<n>`

Search stored documents by semantic similarity to `q`. `top_k` is
optional, defaults to 5.

```json
[
  {
    "id": 1,
    "title": "RCS Thruster Firing Procedure",
    "content": "...",
    "score": 0.56
  }
]
```

### `DELETE /documents/{id}`

Deletes a document by id. Returns `204 No Content` on success, `404` if the id doesn't exist.

## Project structure
```
app/
├── database.py    # SQLAlchemy engine, session, get_db dependency
├── models.py      # Document ORM model (the database table shape)
├── schemas.py     # Pydantic request/response models (the API shape)
├── embeddings.py  # Embedding model singleton, encode/serialize helpers
├── search.py      # Cosine similarity + ranking logic
└── main.py        # FastAPI app and route definitions
tests/
└── test_documents.py
```
Each file has a single responsibility. Routes in `main.py` are
intentionally thin — they validate input, delegate to `embeddings.py`/
`search.py`/the database layer, and shape the response. No embedding or
similarity logic lives in the route handlers themselves.

The embedding model is loaded once, at process startup, rather than per
request — loading it takes roughly 30 seconds, so reusing one instance
across all requests is essential.

## Testing

```bash
pytest -v
```

7 tests, covering:
- Semantic search returns the genuinely relevant document, ranked first
  (the core correctness check, not just "did the endpoint respond")
- `top_k` correctly limits and orders results
- Deleting a document removes it from subsequent search results
- Invalid input (empty title, empty search query) is rejected with `422`
- Deleting a nonexistent id returns `404`
- The API response never leaks the internal embedding vector

Tests run against an isolated, throwaway SQLite database (via FastAPI's
dependency override system) — they never touch the working
`documents.db` created when you run the app normally.

## Design notes

- **Why SQLite + manual cosine similarity instead of a vector database:**
  out of scope per the brief, and unnecessary at this scale — a linear
  scan over a handful of documents is effectively instant.
- **Why sync SQLAlchemy instead of async:** the workload here is
  CPU-bound (computing embeddings), not I/O-bound, so async wouldn't
  improve throughput — it would only add boilerplate across every layer.
- **Why a flat `app/` structure with no sub-folders:** the project has
  one file per concern (one routes file, one models file, etc.) —
  nested folders like `services/` or `routers/` earn their place with
  *multiple* files of the same kind, which this project doesn't have.