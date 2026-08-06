# ADS implementation map

The repository follows the ADS module boundary: API routers only call Workspace-facing services; document parsing and retrieval are deterministic; only `services/ai.py` constructs prompts and calls the inference adapter; raw documents and artifacts are UUID-addressed within the configured workspace root.

The current release implements the Phase 0–4 MVP path: project workspace, durable jobs, supported document ingestion, grounded streaming chat, and versioned Markdown reports. Tesseract is installed in the backend container for image/scanned-PDF extraction. The vector-store provider seam and OpenAI-compatible provider adapter are included; hybrid vector indexing, PPTX/diagram rendering, and knowledge-graph UI remain the next phases of the ADS rather than being represented by misleading stub UI.
