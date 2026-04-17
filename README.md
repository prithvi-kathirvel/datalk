# Datalk Python Engine

Datalk Python Engine is a production-grade, modular SQL agent built using **LangGraph** and **FastAPI**. It leverages natural language processing to translate user queries into SQL, validates them for safety and relevance, executes them against a database, and generates human-readable responses.

## Features

- **Modular Graph Architecture**: Built with LangGraph for robust state management and conditional routing.
- **Production-Ready Persistence**: Uses PostgreSQL (`AsyncPostgresSaver`) for persistence and session management.
- **Advanced SQL Agent**:
    - **Relevance Check**: Ensures queries are related to the database schema.
    - **Dynamic Schema Fetching**: Automatically retrieves relevant table schemas.
    - **Safety Checker**: Regex and LLM-based validation to prevents harmful SQL execution.
    - **Token Tracking**: Integrated monitoring of token usage and costs.
- **High Performance**: Asynchronous implementation using `FastAPI`, `asyncpg`, and `uvicorn`.
- **Multi-Model Support**: Flexible integration with Google Vertex AI, OpenAI, Groq, and more via LangChain.
- **Structured Logging**: Uses `structlog` for comprehensive observability.

## 📁 Project Structure

```text
datalk-python-engine/
├── app/
│   ├── api/             # FastAPI routers and endpoints
│   ├── core/            # Configuration, logging, and middleware
│   ├── db/              # Database connection and pooling logic
│   ├── langgraph/       # Core agent logic
│   │   ├── nodes/       # Functional nodes (get_tables, sql_generator, etc.)
│   │   ├── utils/       # History and state utilities
│   │   └── graph.py     # StateGraph definition and compilation
│   ├── services/        # Business logic (LLM, DB, Sessions)
│   ├── schema/          # Pydantic models for API and state
│   └── main.py          # FastAPI application entry point
├── scripts/             # Utility scripts
├── tests/               # Unit and integration tests
├── .env.example         # Template for environment variables
└── pyproject.toml       # Project dependencies and metadata
```

## Tech Stack

- **Framework**: FastAPI
- **LLM Orchestration**: LangGraph, LangChain
- **Database**: PostgreSQL (Persistence), SQLAlchemy/asyncpg (Execution)
- **Logging**: Structlog
- **Environment**: Pydantic Settings, python-dotenv

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (optional, for specific checkpointers)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd datalk-python-engine
   ```

2. **Set up environment variables**:
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Update the variables with your credentials
   ```

3. **Install dependencies**:
   Using `uv` (recommended):
   ```bash
   uv sync
   ```
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

##  API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/v1/chat` | Send a message to the SQL agent and get a response. |
| `GET` | `/health` | Check application health status. |

## Safety & Security

The engine includes a dedicated `SafetyChecker` node that validates generated SQL queries against common attack patterns and ensures they only perform `SELECT` operations unless explicitly permitted.

## Observability

State transitions and LLM calls are logged via `structlog`. The application is fully compatible with **LangSmith** for deep tracing and debugging of the agentic workflows.
