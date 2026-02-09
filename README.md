<p align="center">
  <h1 align="center">SEOZoom MCP Server</h1>
  <p align="center">
    Server MCP che espone le API di <a href="https://www.seozoom.it/">SEOZoom</a> come tool per Claude Desktop, Claude Code, Cursor e altri client MCP compatibili.
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/tools-25-orange" alt="Tools">
    <img src="https://img.shields.io/badge/transport-stdio-lightgrey" alt="Transport">
  </p>
</p>

---

## Quick Start

**Requisiti:** [Python 3.12+](https://www.python.org/) e [uv](https://docs.astral.sh/uv/)

#### 1. Clona e installa

```bash
git clone https://github.com/Sozione/seozoom-mcp.git
cd seozoom-mcp
uv sync
```

#### 2. Configura

Aggiungi la seguente configurazione JSON nel file corretto in base al client che usi.

> Sostituisci `/path/to/seozoom-mcp` con il percorso reale e `la-tua-api-key` con la tua API key SEOZoom (la trovi nel tuo [profilo SEOZoom](https://www.seozoom.it/)).

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

**Claude Code** — scegli dove metterlo:

| File | Effetto |
|:---|:---|
| `.mcp.json` nella root del progetto | Attivo solo in quel progetto |
| `~/.claude/claude_code_config.json` | Attivo su tutti i progetti |

**Claude Desktop** — aggiungi la configurazione in:

| OS | File |
|:---|:---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

> Se il file non esiste, crealo. Se esiste gia, aggiungi `"seozoom": { ... }` dentro `"mcpServers"`.

#### 3. Avvia

- **Claude Code**: apri il terminale e verifica con `/mcp` che il server sia attivo
- **Claude Desktop**: riavvia l'app, il server apparira nella lista dei tool

> Il server si avvia e si chiude automaticamente con Claude. Non serve gestirlo manualmente.

---

## Guida all'uso in Claude Code

Una volta configurato, puoi chiedere a Claude qualsiasi cosa riguardi la SEO e lui usera automaticamente i tool SEOZoom. Alcuni esempi:

**Analisi keyword**
```
Quali sono le metriche per la keyword "regime forfettario"?
Trova le keyword correlate a "partita iva"
Mostrami la SERP per "calcolatore tasse forfettario"
```

**Analisi dominio**
```
Analizza il dominio repubblica.it
Quali sono le migliori pagine di corriere.it?
Chi sono i competitor organici di aranzulla.it?
Mostrami le keyword per cui ilsole24ore.it appare nelle AI Overview
```

**Analisi URL**
```
Quante keyword ha posizionato questa pagina? https://example.com/pagina
Qual e il Page Zoom Authority di questa URL?
Trova le keyword con potenziale non sfruttato per questa URL
```

**Gestione progetti**
```
Mostrami la lista dei miei progetti SEOZoom
Qual e la panoramica del progetto 190197?
Quali pagine del mio progetto stanno perdendo traffico?
```

**Monitoraggio costi**
```
Quante unita API mi restano?
```

> Non serve specificare quale tool usare: Claude sceglie automaticamente quello giusto in base alla domanda.

---

## Variabili d'ambiente

| Variabile | Obbligatoria | Default | Descrizione |
|:---|:---:|:---:|:---|
| `SEOZOOM_API_KEY` | Si | — | API key dal profilo SEOZoom |
| `SEOZOOM_DEFAULT_DB` | No | `it` | Database paese: `it` `es` `fr` `de` `uk` |

---

## Tool disponibili (25)

Ogni risposta include automaticamente il costo della chiamata:

```
[Costo: 10 unit | Rimanenti: 4950 | Risultati: 1]
```

### Keywords — 4 tool

| Tool | Parametri | Descrizione |
|:---|:---|:---|
| `keyword_metrics` | keywords, db? | Volume di ricerca, KD, CPC, intent, trend mensili |
| `keyword_serp` | keywords, db? | Risultati SERP attuali (fino a 50 risultati) |
| `keyword_serp_history` | keyword, date, db? | Snapshot storico SERP per una data |
| `keyword_related` | keyword, db?, limit? | Keyword correlate con affinita SERP |

### Domains — 8 tool

| Tool | Parametri | Descrizione |
|:---|:---|:---|
| `domain_metrics` | domains, db? | Traffico stimato, keyword posizionate, ZA |
| `domain_metrics_history` | domains, date, db? | Metriche storiche per una data |
| `domain_authority` | domains, db? | Zoom Authority, Trust, Stability, Opportunity |
| `domain_niches` | domains, db?, limit? | Nicchie tematiche con topical authority |
| `domain_best_pages` | domain, db?, limit? | Pagine migliori con PZA |
| `domain_ai_keywords` | domain, db?, offset?, limit? | Keyword nelle AI Overview di Google |
| `domain_keywords` | domain, type, db?, offset?, limit? | Keyword filtrate per tipo |
| `domain_competitors` | domains, db?, limit? | Competitor organici |

Tipi per `domain_keywords`: `best` `withtraffic` `up` `down` `stable` `entered` `exited` `bypage` `byposition` `newentry`

### URLs — 4 tool

| Tool | Parametri | Descrizione |
|:---|:---|:---|
| `url_page_authority` | url, db? | Page Zoom Authority (PZA) |
| `url_metrics` | urls, db? | Keyword totali, traffico, PZA |
| `url_keywords` | url, db?, limit? | Keyword posizionate con volumi e CPC |
| `url_intent_gap` | url, db?, limit? | Keyword con potenziale non sfruttato |

### Projects — 8 tool

| Tool | Parametri | Descrizione |
|:---|:---|:---|
| `project_list` | db? | Lista tutti i progetti |
| `project_overview` | id, db? | Panoramica completa del progetto |
| `project_keywords` | id, db? | Keyword monitorate |
| `project_best_pages` | id, db?, limit? | Migliori pagine del progetto |
| `project_pages_with_more_keywords` | id, db?, limit? | Pagine con piu keyword |
| `project_pages_with_potential` | id, db?, limit? | Pagine con potenziale di crescita |
| `project_winner_pages` | id, db?, limit? | Pagine in crescita |
| `project_loser_pages` | id, db?, limit? | Pagine in calo |

### Utility — 1 tool

| Tool | Parametri | Descrizione |
|:---|:---|:---|
| `check_units` | — | Controlla le unita API rimanenti (costa 10 unit) |

---

## Test con MCP Inspector

```bash
SEOZOOM_API_KEY=la-tua-api-key uv run mcp dev src/seozoom_mcp/server.py
```

---

## API SEOZoom

Documentazione ufficiale: **[apidoc.seozoom.it](https://apidoc.seozoom.it/)**

| | |
|:---|:---|
| Costo per chiamata | 10–120 unita per riga |
| Database supportati | `it` `es` `fr` `de` `uk` |

---

## Come e stato creato

### Setup progetto

Inizializzato con `uv init`, che crea `pyproject.toml` e il virtualenv `.venv`.

### Dipendenze

```toml
[project]
dependencies = [
    "mcp[cli]",   # SDK MCP con FastMCP
    "httpx",      # Client HTTP async
]

[project.scripts]
seozoom-mcp = "seozoom_mcp.server:main"
```

- **`mcp[cli]`** — SDK ufficiale del Model Context Protocol, include `FastMCP` per creare server in modo dichiarativo
- **`httpx`** — Client HTTP asincrono, necessario perche i tool MCP sono funzioni `async`

### Client HTTP (`client.py`)

Classe `SEOZoomClient` che wrappa le API REST di SEOZoom v2:

- Base URL: `https://apiv2.seozoom.com/api/v2`
- Autenticazione: `api_key` come query parameter
- Tutti gli endpoint sono GET con `action` come query parameter
- I valori multipli (keyword, domini, URL) sono separati da pipe `|`
- Un metodo per ogni endpoint, che restituisce il JSON di risposta

### Server MCP (`server.py`)

Creato con `FastMCP`, il framework dichiarativo dell'SDK MCP:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("seozoom")

@mcp.tool()
async def keyword_metrics(
    keywords: Annotated[list[str], "Lista di keyword (max 100)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni metriche per una o piu keyword."""
    return _fmt(await client.keyword_metrics(keywords, db))
```

Ogni tool:
- Ha type hints `Annotated` con descrizioni per l'LLM
- Ha un docstring che l'LLM usa per capire quando invocarlo
- Restituisce JSON come stringa
- Delega la chiamata HTTP al `SEOZoomClient`

### Trasporto

Il server usa il trasporto **stdio** (standard input/output), compatibile con Claude Desktop, Claude Code e Cursor. Il client MCP lancia il processo e comunica via stdin/stdout con messaggi JSON-RPC.

---

## License

MIT
