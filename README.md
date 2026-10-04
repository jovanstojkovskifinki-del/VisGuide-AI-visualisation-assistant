# VisGuide

**AI-powered interactive data visualization.** Upload structured data, and VisGuide picks the clearest way to show it — then lets you refine it in plain English.

> Given any type of information, determine the most appropriate way for a human to understand it.

This is the guiding philosophy behind VisGuide. Module 1 (the current focus, documented here) implements that for structured tabular data. Future modules (see [Roadmap](#roadmap)) extend it to PDFs, 3D scenes, audio, and more.

---

## What it does

1. **Upload** a CSV or Excel file.
2. VisGuide **parses** it, detects each column's type (numeric, categorical, datetime, boolean, latitude/longitude, identifier), and profiles data quality (row/column counts, duplicates).
3. A **recommendation engine** picks the single best chart type for the data and explains why, with a confidence score.
4. The frontend renders the chart (via Plotly) from a standardized config the backend produces — **the backend never renders charts itself**.
5. An **AI chat panel** lets you refine the result in natural language: change chart type, filter or group the data, switch axes, or ask for real statistics (mean, correlation, percentages, outliers, etc.) computed directly from your actual data — not guessed by the model.

---

## Architecture

Django project following **Clean Architecture / SOLID**: business logic lives in `domain`/`application` layers, not in views. Each app that has real logic (`chat`, and eventually others) follows this layout:

```
apps/<app>/
├── domain/            # entities, interfaces — no framework dependencies
├── application/        # use cases that orchestrate domain + infrastructure
├── infrastructure/      # concrete implementations (LLM calls, pandas, DB)
├── api/                 # DRF views & serializers — thin, delegate to use cases
├── models.py
└── urls.py
```

### Apps

| App | Responsibility |
|---|---|
| `apps.datasets` | Upload, storage, and parsing of CSV/Excel files. `Dataset` (UUID PK, `FileField`, `FileType`) and `DatasetColumn` (structural column snapshot + sample values) live here. |
| `apps.analysis` | Column-type detection and data-quality profiling. |
| `apps.recommendations` | Decides which chart type fits the data. Originally rule-based; now backed by an LLM (Groq), designed to be swappable. |
| `apps.visualizations` | Builds the standardized visualization config object served to the frontend. |
| `apps.chat` | The AI chat feature — see below. |
| `apps.core` | Shared enums (`FileType`, `DatasetStatus`) and cross-app interfaces. |

### Visualization config contract

The frontend (`index.html`, vanilla JS + Plotly) expects:

```json
{
  "visualizationType": "BAR_CHART",
  "xAxis": { "column": "region", "label": "Region" },
  "yAxis": { "column": "sales", "label": "Sales" },
  "options": { "binCount": 20 },
  "metadata": { "correlationMatrix": { "matrix": [[...]], "columns": [...] } },
  "filters": [ { "column": "age", "operator": "gte", "value": "30" } ],
  "aggregatedData": { "x": [...], "y": [...], "aggregation": "mean" }
}
```

Supported `visualizationType` values: `LINE_CHART`, `BAR_CHART`, `SCATTER_PLOT`, `HISTOGRAM`, `HEATMAP`, `GEOGRAPHIC_MAP`, `CHOROPLETH_MAP`, `TABLE` (fallback).

---

## The AI chat feature (`apps/chat`)

The most substantial piece beyond core Module 1. The chat lets users control the visualization and query real statistics through natural language, using LLM tool-calling.

### Tools exposed to the model

| Tool | Does |
|---|---|
| `change_chart_type` | Switch chart type (`bar`, `line`, `scatter`, `histogram`, `heatmap`, `map`). For `heatmap`, computes a **real** pandas correlation matrix. |
| `group_by` | Groups rows by a column and aggregates a numeric column (`sum`/`mean`/`count`/`min`/`max`) — real server-side pandas computation, not a client-side approximation. |
| `filter_data` | Real server-side row filtering (`eq`, `neq`, `gt`, `lt`, `gte`, `lte`, `contains`, `between`). Multiple calls AND together. |
| `clear_filters` / `remove_filter` | Reset all filters, or remove one by index — the latter available as a direct UI action (see below), no LLM call needed. |
| `set_axes` | Set x/y axis columns. |
| `compute_statistic` | Real statistics via pandas: `mean`, `median`, `mode`, `sum`, `count`, `min`, `max`, `std`, `variance`, `unique_count`, `missing_count`, `percentage` (with optional category isolation), `outlier_count` (IQR method). |

The model also receives a **computed "top correlated column pairs" summary** as context, so it can answer "which columns are most related" without guessing or chaining extra calls.

### Design decisions worth knowing

- **Multiple tool calls per turn are applied in sequence**, not overwritten — e.g. "make a bar chart with X and Y" triggers `change_chart_type` + `set_axes` together, both applied.
- **Deterministic UI actions bypass the LLM.** Clicking a filter chip's × or "Clear filters" hits a separate `apply-command` endpoint that runs the same executor directly — no model call, no quota spent, no latency.
- **Multi-model fallback.** Chat requests try a chain of models (currently Groq `openai/gpt-oss-120b` → `openai/gpt-oss-20b` → local Ollama `llama3.1`, see `apps/chat/infrastructure/llm/model_registry.py`), automatically skipping any that hit a rate limit (tracked with a cooldown) or are unreachable. The frontend shows which model answered and lets the user force a specific one.
- **Chat history is capped** (`MAX_HISTORY_MESSAGES`, currently 20) before being sent to the model, to avoid exceeding context-length limits on long conversations. Nothing is deleted from the database — only what's replayed to the LLM is windowed.
- **Statistics are never hallucinated.** Every number in a chat reply comes from `PandasStatisticsService` running against the actual uploaded file, not from the LLM's own arithmetic.

### API endpoints (chat)

| Method & path | Purpose |
|---|---|
| `POST /api/datasets/<uuid:dataset_id>/messages/` | Send a chat message. Body: `{ message, current_config, data_schema, preferred_model? }`. Returns `{ reply, updated_config, model_used, model_status }`. |
| `POST /api/datasets/<uuid:dataset_id>/apply-command/` | Apply a deterministic command directly (no LLM). Body: `{ command_type, params, current_config, data_schema }`. |
| `GET /api/models/` | Current status of every registered model (`available` / `cooling_down` + retry time). |

---

## Frontend

Single-file `index.html` — vanilla JS, no build step, Plotly for rendering. Dark, mono/display-font aesthetic (amber/cyan/violet/green accents on a near-black base), restyled to a light-background variant as well.

Key UI pieces:
- Upload dropzone → readout panel (column types, row/dupe counts) → recommendation panel (confidence dial, reasoning) → chart → chat.
- **State bar**: live chips showing the active chart type and filters, each filter removable individually.
- **Chat panel**: model selector + "answered by" badge, typing indicator, chart-update flash, quick-start suggestion chips.

---

## Setup

### Requirements
- Python 3.12, Django + DRF
- pandas (for the chat feature's real data access)
- A free [Groq](https://console.groq.com) API key
- (Optional) [Ollama](https://ollama.com) running locally as an ultimate fallback model

### Environment variables
```
GROQ_API_KEY=<your-key>
```

### Run
```powershell
python manage.py migrate
python manage.py runserver
```

Visit `http://localhost:8000/`.

---

## Known limitations

- `ChatSession` is per-dataset, not per-user — there's no auth layer yet, so "collaborative chat" in the roadmap below needs that first.
- The model-cooldown tracker is an in-memory dict — fine for a single dev-server process, would need a shared cache/DB behind multiple workers.
- `group_by` only groups by the first column if multiple are given (multi-column grouping not yet implemented).
- No automated test suite yet for the executor/statistics logic.

---

## Roadmap

Beyond Module 1:
- **PDF / textbook visualization** — concept extraction, knowledge graphs
- **3D visualization module** — concepts mapped to Three.js scene configs
- **Audio visualization**
- **Vector database** — ground the AI assistant in uploaded documents, not just tabular data
- **Collaborative AI chat** — multi-user sessions (needs auth first)
