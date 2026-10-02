# Aisle Project Roadmap & Kanban Board

This document tracks future scopes, issues, and architectural improvements planned for the Aisle multi-agent platform.

---

## 📋 Kanban Board

| Backlog (Proposed) | To Do (Planned) | In Progress | Done (Implemented) |
| :--- | :--- | :--- | :--- |
| | | | • **Issue #1**: Persistent Profile DB Table<br>• **Issue #2**: SSE Node Latency UI<br>• **Issue #3**: LangSmith Evaluation Suite<br>• **Issue #4**: Docker Secrets & Prod Security<br>• **Issue #5**: Dynamic Model Degradation & Deployment Setup |

---

## 🛠️ Completed Issues & Scopes

### 🟢 Issue #1: Persistent Customer Memory & Profile DB
* **Status:** Done
* **Description:** Migrated `CustomerMemory` from in-memory dictionary to SQLModel database persistence (`CustomerProfile` table) with async CRUD operations.

---

### 🟢 Issue #2: SSE Node Latency Visualizations
* **Status:** Done
* **Description:** Calculated node execution duration (`elapsed_ms`) in `app/api.py` during Server-Sent Event (SSE) streaming and updated Next.js `pipeline-visualizer.tsx` to render real-time latency badges (`8ms`, `1.4s`).

---

### 🟢 Issue #3: LangSmith Evaluation Suite
* **Status:** Done
* **Description:** Built `tests/eval_suite.py` LLMOps benchmark runner to evaluate supervisor routing accuracy (100%), PII redaction speed, and response quality.

---

### 🟢 Issue #4: Container Secrets Management
* **Status:** Done
* **Description:** Configured `app/config.py` `Settings` to load API keys and JWT secrets from `/run/secrets/` Docker Secrets files and declared secrets in `docker-compose.yml`.

---

### 🟢 Issue #5: Dynamic Model Degradation & Deployment Setup
* **Status:** Done
* **Description:** Configured budget alert thresholds to automatically trigger dynamic model degradation (swapping to low-cost `gemini-3.5-flash-lite` at 80% capacity) and added flexible `AsyncPostgresSaver` checkpointer support.
