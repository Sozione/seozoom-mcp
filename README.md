# SEOZoom MCP Server

Server MCP (Model Context Protocol) che espone le API di SEOZoom come tool utilizzabili da Claude Desktop, Claude Code, Cursor e altri client MCP compatibili.

## Requisiti

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- API key SEOZoom (ottenibile dal proprio profilo su seozoom.it)

## Installazione

```bash
git clone <repo-url>
cd seozoom-mcp
uv sync
```

## Configurazione

### Variabili d'ambiente

| Variabile | Obbligatoria | Default | Descrizione |
|-----------|:---:|---------|-------------|
| `SEOZOOM_API_KEY` | Si | - | API key dal profilo SEOZoom |
| `SEOZOOM_DEFAULT_DB` | No | `it` | Database paese: `it`, `es`, `fr`, `de`, `uk` |

### Claude Code

Crea un file `.mcp.json` nella root del progetto in cui lavori (o nella root di `seozoom-mcp`):

```json
{
  "mcpServers": {
    "seozoom": {
      "command": "uv",
      "args": ["--directory", "/path/to/seozoom-mcp", "run", "seozoom-mcp"],
      "env": {
        "SEOZOOM_API_KEY": "la-tua-api-key"
      }
    }
  }
}
```

Al primo avvio, Claude Code chiederà di approvare il server. Verifica con `/mcp` che sia attivo.

### Claude Desktop

Aggiungi in `claude_desktop_config.json` (su macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "seozoom": {
      "command": "uv",
      "args": ["--directory", "/path/to/seozoom-mcp", "run", "seozoom-mcp"],
      "env": {
        "SEOZOOM_API_KEY": "la-tua-api-key"
      }
    }
  }
}
```

### Test con MCP Inspector

```bash
SEOZOOM_API_KEY=la-tua-api-key uv run mcp dev src/seozoom_mcp/server.py
```

## Struttura progetto

```
seozoom-mcp/
├── pyproject.toml              # Dipendenze e entry point
└── src/
    └── seozoom_mcp/
        ├── __init__.py
        ├── client.py           # Client HTTP async per le API SEOZoom
        └── server.py           # Server FastMCP con 25 tool
```

## Tool disponibili (25)

### Keywords (4)

| Tool | Parametri | Descrizione |
|------|-----------|-------------|
| `keyword_metrics` | keywords, db? | Volume di ricerca, KD, CPC, intent, trend mensili |
| `keyword_serp` | keywords, db? | Risultati SERP attuali (fino a 50 risultati) |
| `keyword_serp_history` | keyword, date, db? | Snapshot storico SERP per una data |
| `keyword_related` | keyword, db?, limit? | Keyword correlate con affinità SERP |

### Domains (8)

| Tool | Parametri | Descrizione |
|------|-----------|-------------|
| `domain_metrics` | domains, db? | Traffico stimato, keyword posizionate, ZA |
| `domain_metrics_history` | domains, date, db? | Metriche storiche per una data |
| `domain_authority` | domains, db? | Zoom Authority, Trust, Stability, Opportunity |
| `domain_niches` | domains, db?, limit? | Nicchie tematiche con topical authority |
| `domain_best_pages` | domain, db?, limit? | Pagine migliori con PZA |
| `domain_ai_keywords` | domain, db?, offset?, limit? | Keyword nelle AI Overview di Google |
| `domain_keywords` | domain, type, db?, offset?, limit? | Keyword filtrate per tipo |
| `domain_competitors` | domains, db?, limit? | Competitor organici |

**Tipi per `domain_keywords`**: `best`, `withtraffic`, `up`, `down`, `stable`, `entered`, `exited`, `bypage`, `byposition`, `newentry`

### URLs (4)

| Tool | Parametri | Descrizione |
|------|-----------|-------------|
| `url_page_authority` | url, db? | Page Zoom Authority (PZA) |
| `url_metrics` | urls, db? | Keyword totali, traffico, PZA |
| `url_keywords` | url, db?, limit? | Keyword posizionate con volumi e CPC |
| `url_intent_gap` | url, db?, limit? | Keyword con potenziale non sfruttato |

### Projects (8)

| Tool | Parametri | Descrizione |
|------|-----------|-------------|
| `project_list` | db? | Lista tutti i progetti |
| `project_overview` | id, db? | Panoramica completa del progetto |
| `project_keywords` | id, db? | Keyword monitorate |
| `project_best_pages` | id, db?, limit? | Migliori pagine del progetto |
| `project_pages_with_more_keywords` | id, db?, limit? | Pagine con più keyword |
| `project_pages_with_potential` | id, db?, limit? | Pagine con potenziale di crescita |
| `project_winner_pages` | id, db?, limit? | Pagine in crescita |
| `project_loser_pages` | id, db?, limit? | Pagine in calo |

### Utility (1)

| Tool | Parametri | Descrizione |
|------|-----------|-------------|
| `check_units` | - | Controlla le unità API rimanenti (costa 10 unit) |

### Tracking costi

Ogni risposta include automaticamente un header con il consumo:

```
[Costo: 10 unit | Rimanenti: 4950 | Risultati: 1]
```

## Come è stato creato

### 1. Setup progetto

Inizializzato con `uv init`, che crea `pyproject.toml` e il virtualenv `.venv`.

### 2. Dipendenze

```toml
[project]
dependencies = [
    "mcp[cli]",   # SDK MCP con FastMCP
    "httpx",      # Client HTTP async
]

[project.scripts]
seozoom-mcp = "seozoom_mcp.server:main"
```

- **`mcp[cli]`**: SDK ufficiale del Model Context Protocol, include `FastMCP` per creare server in modo dichiarativo
- **`httpx`**: Client HTTP asincrono, necessario perché i tool MCP sono funzioni `async`

### 3. Client HTTP (`client.py`)

Classe `SEOZoomClient` che wrappa le API REST di SEOZoom v2:

- Base URL: `https://apiv2.seozoom.com/api/v2`
- Autenticazione: `api_key` come query parameter
- Tutti gli endpoint sono GET con `action` come query parameter
- I valori multipli (keyword, domini, URL) sono separati da pipe `|`
- Un metodo per ogni endpoint, che restituisce il JSON di risposta

### 4. Server MCP (`server.py`)

Creato con `FastMCP`, il framework dichiarativo dell'SDK MCP:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("seozoom")

@mcp.tool()
async def keyword_metrics(
    keywords: Annotated[list[str], "Lista di keyword (max 100)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni metriche per una o più keyword: volume di ricerca, KD, CPC, intent e trend mensili."""
    return _fmt(await client.keyword_metrics(keywords, db))
```

Ogni tool:
- Ha type hints `Annotated` con descrizioni per l'LLM
- Ha un docstring che l'LLM usa per capire quando invocarlo
- Restituisce JSON come stringa
- Delega la chiamata HTTP al `SEOZoomClient`

### 5. Trasporto

Il server usa il trasporto **stdio** (standard input/output), compatibile con Claude Desktop, Claude Code e Cursor. Il client MCP lancia il processo e comunica via stdin/stdout con messaggi JSON-RPC.

### 6. API SEOZoom v2

Documentazione: [apidoc.seozoom.it](https://apidoc.seozoom.it/)

Ogni endpoint ha:
- Un **costo in unità API** (10-120 per riga)
- Un **rate limit** (10-150 richieste/minuto)
- Un **numero massimo di righe** per risposta
- Database paese supportati: `it`, `es`, `fr`, `de`, `uk`

Crediti giornalieri gratuiti: 6.500 unità API.
