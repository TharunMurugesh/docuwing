# Docuwing

Local-first, document-grounded AI workspace implemented from the approved ADS.

## Run

```bash
docker compose up --build
docker compose exec ollama ollama pull qwen2.5:7b-instruct
docker compose exec ollama ollama pull nomic-embed-text
```

Open `http://localhost:3000`. The API is documented at `http://localhost:8000/docs`.

For NVIDIA GPU use `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build`.

## Implemented boundaries

- Workspace: projects, documents, chat sessions, messages, results and jobs in SQLite.
- Knowledge: background deterministic ingestion, format parsers, structure-aware chunking, project-scoped lexical retrieval.
- AI: an Ollama provider adapter and prompt boundary that treats document content as data.
- Execution: durable ingestion jobs and SSE progress, plus a fixed, dependency-aware tool registry/runner that admits no general code or file-system execution.
- Artifacts: immutable, versioned Markdown report output on report/export requests.

Data is persisted under the `docuwing-data` Docker volume (or `DOCUWING_STORAGE_ROOT` when run directly). No cloud provider is configured by default.
