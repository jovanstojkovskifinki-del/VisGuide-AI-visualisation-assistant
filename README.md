# VisGuide — AI Visualisation Assistant

VisGuide turns a spreadsheet into the clearest possible chart, then lets you refine it by simply talking to it.

Upload a CSV or Excel file and VisGuide will:

1. **Read and profile it** — detect what type each column is (numeric, categorical, date, location, etc.) and check basic data quality (row/column counts, duplicates).
2. **Recommend a chart** — pick the view that best fits your data (bar, line, scatter, histogram, correlation heatmap, map…) and explain why, with a confidence score.
3. **Let you steer it in plain English** — an AI chat panel can change the chart, filter or group your data, and calculate real statistics (averages, correlations, percentages, outliers). Every number comes from your actual file, computed with pandas — never guessed by the AI.

## How it works

- **Backend (Django + Django REST Framework)** parses the file, analyses it, and produces a standard chart configuration. It never draws charts itself.
- **Frontend (a single `index.html` using Plotly)** takes that configuration and renders it in the browser.
- **AI chat** uses an LLM through the free [Groq](https://console.groq.com) API. The model chooses *what* to do (e.g. "filter to the last 5 years, show a bar chart"), and the backend does the actual work on your data. If one model is busy or rate-limited, VisGuide automatically switches to the next one, and shows you which model answered.

---

## Getting started

### 1. Prerequisites

- **Python 3.12** (3.10+ should also work)
- **Git**
- A free **Groq API key** (for the AI chat) — create one at <https://console.groq.com>

### 2. Download the project

```bash
git clone https://github.com/jovanstojkovskifinki-del/VisGuide-AI-visualisation-assistant.git
cd VisGuide-AI-visualisation-assistant
```

Then move into the folder that contains `manage.py` (if it isn't the repository root).

### 3. Create a virtual environment and install dependencies

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

If the repository has no `requirements.txt`, install the core packages directly:

```bash
pip install django djangorestframework pandas openpyxl requests
```

### 4. Add your Groq API key

The AI chat reads the key from an environment variable. Set it in the same terminal you will run the server from.

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY = "your-key-here"
```

**macOS / Linux:**
```bash
export GROQ_API_KEY="your-key-here"
```

> The key is only set for the current terminal session. Never commit it to GitHub.

### 5. Set up the database and start the server

```bash
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser.

---

## Using VisGuide

1. **Upload** — drag a `.csv` or `.xlsx` file onto the upload box (or click it to browse).
2. **Check the readout** — the left panel shows row/column counts, duplicates, and the detected type of every column (colour-coded).
3. **See the recommendation** — the right panel shows the suggested chart, the reason for it, and a confidence dial.
4. **Ask the chat** — use the "Ask VisGuide" box under the chart. Some things to try:
   - *"Make it a bar chart"*
   - *"Show the correlation heatmap"* / *"Which columns are most correlated?"*
   - *"What is the average of Age?"*
   - *"What percentage of rows are High?"*
   - *"Group by Region and show the average Sales"*
   - *"Show only entries from the last 5 years"*
   - *"Are there any outliers in Price?"*
5. **Manage filters** — active filters appear as chips under the chart. Click **×** on a chip to remove one, or **Clear all** to reset.
6. **Pick a model (optional)** — the dropdown in the chat header lets you force a specific AI model. Leave it on *Auto* and VisGuide will switch automatically if a model hits its rate limit.
7. **Inspect the data** — click **View raw data** to see the first 100 rows of the current view.

---

## Optional settings

| Setting | What it does |
|---|---|
| `RECOMMENDATION_ENGINE = "ai"` (in your Django settings) | Uses an AI model, instead of the built-in rule-based engine, to choose the initial chart. Defaults to rule-based. |
| Local [Ollama](https://ollama.com) running on port 11434 | Used as a last-resort fallback model for the chat if the Groq models are unavailable. |

## Troubleshooting

- **"GROQ_API_KEY environment variable is not set"** — set the key (step 4) in the same terminal you start the server from, then restart the server.
- **Chat says every model is cooling down** — the free Groq rate limit was hit; wait a minute and try again.
- **"AI recommendation failed, falling back to TABLE"** in the server log — the AI recommendation engine can't reach its model. Either use the default rule-based engine or make sure the engine is configured for Groq and the API key is set.
- **Upload rejected** — only `.csv` and `.xlsx` files are supported.

## Project layout

```
apps/
├── datasets/          Upload and parsing of CSV/Excel files
├── analysis/          Column-type detection and data profiling
├── recommendations/   Chooses the best chart type
├── visualizations/    Builds the chart configuration sent to the frontend
├── chat/              AI chat: tool-calling, real statistics, model fallback
└── core/              Shared enums and interfaces
config/                Django project settings and URLs
```

The codebase follows Clean Architecture: business logic lives in domain/application layers, kept out of the views.
