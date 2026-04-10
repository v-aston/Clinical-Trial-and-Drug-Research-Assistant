# Clinical Trial and Drug Research Assistant

## Overview

This project is a production oriented Retrieval Augmented Generation (RAG) backend that answers medical research questions using evidence retrieved from real world data sources. The system is designed for the "Clinical Trial Drug Research Assistant" use case by combining data from ClinicalTrials.gov and PubMed, then generating grounded answers with source citations.

The application supports multi-source ingestion, chunking, embedding generation, vector retrieval, and answer generation through a FastAPI backend. It is built to demonstrate clean architecture, scalable service boundaries, and clear documentation of technical decisions and trade-offs.

## Problem Statement

Medical research queries often require evidence from multiple complementary sources. ClinicalTrials.gov provides structured trial records such as trial status, phase, interventions, and outcomes, while PubMed provides abstracts and research literature context. A useful assistant in this domain should retrieve evidence from both sources and generate answers grounded in those sources rather than relying on unsupported LLM recall.

## Scope of This Implementation

- Multi-source ingestion from ClinicalTrials.gov and PubMed.
- Document normalization into a common internal schema.
- Chunking of source documents for retrieval.
- Embedding generation and storage in PostgreSQL with pgvector.
- Retrieval using vector similarity search.
- Answer generation through an LLM using retrieved context.
- Inline source attribution in the response payload.
- Backend API endpoints for ingest, query, and health checks.

## System Architecture

The system follows a layered backend design:

1. Source connectors fetch data from external APIs.
2. An ingestion service normalizes and stores source documents.
3. A chunking service splits long texts into retrieval friendly units.
4. An embedding service generates vector embeddings for chunks.
5. PostgreSQL with pgvector stores embeddings and metadata.
6. A retrieval service embeds the user question and performs similarity search.
7. A query service builds a grounded prompt and calls the LLM.
8. The API returns the answer with citation metadata.

## Architecture Diagram

```text
External Sources
  ├── PubMed
  └── ClinicalTrials.gov
         │
         ▼
   Source Connectors
         │
         ▼
    Ingest Service
         │
         ├── Normalize documents
         ├── Deduplicate
         ├── Chunk content
         └── Generate embeddings
         │
         ▼
 PostgreSQL + pgvector
         │
         ▼
  Retrieval Service
         │
         ▼
    Query Service
         │
         ▼
  LLM Response + Citations
         │
         ▼
     FastAPI API
```

## RAG Pipeline Explanation

### 1. Data Ingestion

The system ingests documents from:
- PubMed through the Entrez API.
- ClinicalTrials.gov through the official study API.

Both connectors transform source specific fields into a unified internal document schema. This makes the downstream ingestion pipeline reusable across sources.

### 2. Document Normalization

Each ingested item is normalized into a shared format containing:
- `external_id`
- `source_type`
- `title`
- `source_url`
- `raw_text`
- `metadata_json`

This normalization allows PubMed papers and ClinicalTrials records to be indexed and queried through the same retrieval pipeline.

### 3. Deduplication

Before inserting a document, the ingestion layer checks whether a record with the same `source_type` and `external_id` already exists. This prevents duplicate inserts, repeated chunk generation, and unnecessary embedding work.

### 4. Chunking Strategy

Documents are split into smaller chunks before embedding. Chunking improves retrieval quality because most user questions align more closely with a focused section of text than with an entire document. Chunking also reduces noise in similarity search and improves citation granularity.

### 5. Embedding Generation

Each chunk is converted into a dense vector embedding using the configured embedding pipeline. These embeddings are stored in PostgreSQL using pgvector so that semantic nearest neighbor search can be performed at query time.

### 6. Vector Storage

Embeddings are stored directly in PostgreSQL using pgvector. This keeps structured metadata and vectors in a single database, simplifies operations, and avoids introducing an external vector database for this scope of work.

### 7. Retrieval Logic

At query time:
- the user question is embedded,
- the embedding is compared against stored chunk embeddings using cosine distance,
- the top matching chunks are selected,
- low-relevance results are filtered using a relevance threshold.

This keeps the context passed to the LLM focused and reduces noise.

### 8. Response Generation

The query service builds a grounded prompt using the retrieved chunks and asks the LLM to answer using only the supplied context. If the evidence is insufficient, the LLM is instructed to explicitly say so rather than invent details. The response includes citations derived from the retrieved chunks.

## API Endpoints

The backend exposes versioned API endpoints under `/api/v1`.

### Health

```http
GET /api/v1/health
```

Purpose:
- confirms the API is running,
- provides a lightweight operational check.

### Ingest

```http
POST /api/v1/ingest
```

Example request:

```json
{
  "source_type": "pubmed",
  "query": "HER2 positive breast cancer",
  "max_documents": 2
}
```

Supported `source_type` values:
- `pubmed`
- `clinicaltrials`

Example response:

```json
{
  "status": "success",
  "source_type": "pubmed",
  "query": "HER2 positive breast cancer",
  "documents_fetched": 2,
  "documents_inserted": 2,
  "chunks_created": 3,
  "embeddings_created": 3
}
```

### Query

```http
POST /api/v1/query
```

Example request:

```json
{
  "question": "What clinical trials are studying HER2 positive breast cancer?",
  "top_k": 3
}
```

Example response:

```json
{
  "answer": "Several sources discuss HER2-positive breast cancer, including clinical trial evidence and review literature [Source 1] [Source 2].",
  "citations": [
    {
      "chunk_id": "chunk_001",
      "document_id": "doc_001",
      "title": "HER2-positive breast cancer",
      "source_type": "pubmed",
      "source_url": "https://pubmed.ncbi.nlm.nih.gov/27939064/",
      "chunk_index": 0,
      "snippet": "Anti-HER2 treatment for HER2-positive breast cancer has changed...",
      "distance": 0.313
    }
  ],
  "retrieved_chunks": 3,
  "cached": false
}
```

## Example Queries

You can use the following queries to demonstrate the system:

- `What clinical trials are studying HER2 positive breast cancer?`
- `What are the current treatment approaches for HER2-positive breast cancer?`
- `What evidence is available on trastuzumab resistance?`
- `Which Phase III studies are relevant to HER2-positive breast cancer?`

## Tech Stack

### Backend
- Python
- FastAPI 

### Database
- PostgreSQL
- pgvector

### AI / Retrieval
- Embedding model via local or configured embedding pipeline
- LLM abstraction: Implemented a provider-agnostic LLM layer to support interchangeable model backends

### External Data Sources
- PubMed
- ClinicalTrials.gov

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL
- pgvector extension enabled
- Required API keys or local model configuration depending on your LLM and embedding setup

### Local Setup

```bash
git clone <your-repository-url>
cd <your-repository-name>

python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Database Initialization

The project uses PostgreSQL with pgvector for relational storage and vector similarity search. Database setup is supported through the `scripts/schema.sql` file, which initializes the required database objects for the application.

The schema script is responsible for:
- enabling the `pgvector` extension,
- creating the core application tables,
- defining relationships between source documents and chunks,
- preparing the database for vector-based retrieval.

Run the schema setup after creating the database:

```bash
psql -U postgres -d rag_db -f scripts/schema.sql
```

If Docker is being used for PostgreSQL, the same script can be applied inside the running container:

```bash
docker exec -i <postgres-container-name> psql -U postgres -d rag_db < scripts/schema.sql
```

This step should be completed before running ingestion or query workflows.

Configure environment variables in `.env` as needed, for example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_db
PUBMED_EMAIL=your_email@example.com
GEMINI_API_KEY=your_gemini_key
```

Run the application:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Docker Setup

Build and run:

```bash
docker-compose up --build
```

## Research and Design Decisions

### Why FastAPI

FastAPI was selected because it provides:
- clear schema validation through Pydantic,
- automatic OpenAPI documentation,
- clean API layering.

This makes it well-suited for a production-style RAG API.

### Why PostgreSQL + pgvector

PostgreSQL with pgvector was chosen because:
- it keeps structured metadata and vector embeddings in a single datastore,
- it avoids introducing an additional managed vector database,
- it is sufficient for the current project scale,
- it supports cosine distance search directly in SQL.

Trade-off:
- dedicated vector databases may provide more advanced retrieval features or scaling paths at much larger volumes.

### Why Multi-Source Ingestion

ClinicalTrials.gov and PubMed complement each other:
- ClinicalTrials.gov provides structured trial data.
- PubMed provides research paper abstracts and biomedical context. 

This combination aligns well with the chosen domain and produces richer evidence for answers.

### Why a Normalized Document Schema

A shared document schema makes the pipeline reusable and simplifies:
- ingestion logic,
- deduplication,
- chunking,
- retrieval,
- citations.

Without normalization, each source would require source-specific handling deep into the pipeline.

### Why Chunking

Embedding entire documents often reduces retrieval precision because relevant evidence may be buried inside much longer text. Chunking improves semantic matching and gives more precise citations.

Trade-off:
- if chunks are too small, context is fragmented;
- if chunks are too large, retrieval becomes noisy.

### Why Relevance Filtering

A relevance threshold was added during retrieval to reduce low quality matches before they are sent to the LLM. This improves answer grounding and helps control noisy context.

### Why a Service-Layered Design

The project separates:
- API routes,
- ingestion orchestration,
- retrieval,
- query handling,
- connector logic.

This makes the codebase easier to test, extend, and reason about.

## Trade-Offs Considered

### Simplicity vs. Advanced Retrieval

This implementation uses dense vector retrieval with cosine distance. It does not yet include hybrid search, reranking, or keyword retrieval. This keeps the system simpler and easier to explain, but may miss some edge cases where keyword-sensitive retrieval would help. 

### Single Database vs. Dedicated Vector Store

Keeping vectors inside PostgreSQL reduces infrastructure complexity, but it may not be optimal for very large-scale, high-throughput semantic search workloads.

### Fast Delivery vs. Full Product Features

The implementation focuses on backend correctness and clean architecture. It does not yet include a frontend UI, advanced observability, streaming responses, or evaluation dashboards.

## Limitations

Current limitations of this implementation include:

- Retrieval is dense vector only and does not yet include hybrid keyword + vector search.
- There is no reranking layer on top of initial retrieval.
- The query flow is primarily single turn and does not yet model longer conversational history.
- Evaluation metrics scoring are not yet implemented.
- No frontend UI is included in this submission.
- The current scope focuses on abstracts and structured records, not full-text article ingestion.
- Guardrails and domain-specific medical disclaimers can be improved further.

## Future Improvements

Suggested future improvements:

- Hybrid search combining keyword search with vector retrieval. 
- Reranking of retrieved chunks before prompt assembly. 
- More formal retrieval and answer evaluation metrics. 
- Streaming responses for better UX. 
- Conversation memory or session-aware querying. 
- Better guardrails for hallucination handling. 
- Multi-document reasoning improvements across several retrieved sources. 
- UI layer for easier ingestion and querying demos.
- Observability and structured logging for production monitoring.
- Background ingestion jobs for larger datasets.
