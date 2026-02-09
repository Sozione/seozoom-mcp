from __future__ import annotations

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP

from seozoom_mcp.client import SEOZoomClient

mcp = FastMCP("seozoom")
client = SEOZoomClient()


def _fmt(data: object) -> str:
    if isinstance(data, dict) and "UnitsUsed" in data:
        used = data.get("UnitsUsed", "?")
        remaining = data.get("UnitsRemaining", "?")
        rows = data.get("ResultRows", "?")
        header = f"[Costo: {used} unit | Rimanenti: {remaining} | Risultati: {rows}]\n\n"
        return header + json.dumps(data.get("response", data), ensure_ascii=False, indent=2)
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── Keywords ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def keyword_metrics(
    keywords: Annotated[list[str], "Lista di keyword (max 100)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni metriche per una o più keyword: volume di ricerca, KD, CPC, intent e trend mensili."""
    return _fmt(await client.keyword_metrics(keywords, db))


@mcp.tool()
async def keyword_serp(
    keywords: Annotated[list[str], "Lista di keyword (max 100)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni i risultati SERP attuali (fino a 50 risultati organici) per una o più keyword."""
    return _fmt(await client.keyword_serp(keywords, db))


@mcp.tool()
async def keyword_serp_history(
    keyword: Annotated[str, "Singola keyword"],
    date: Annotated[str, "Data nel formato yyyy-MM-dd"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni lo snapshot storico della SERP per una keyword in una data specifica."""
    return _fmt(await client.keyword_serp_history(keyword, date, db))


@mcp.tool()
async def keyword_related(
    keyword: Annotated[str, "Singola keyword"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di keyword correlate"] = None,
) -> str:
    """Ottieni keyword correlate con volume di ricerca e affinità SERP (0-100)."""
    return _fmt(await client.keyword_related(keyword, db, limit))


# ── Domains ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def domain_metrics(
    domains: Annotated[list[str], "Lista di domini (max 50)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni metriche dettagliate per uno o più domini: traffico stimato, keyword posizionate, ZA."""
    return _fmt(await client.domain_metrics(domains, db))


@mcp.tool()
async def domain_metrics_history(
    domains: Annotated[list[str], "Lista di domini (max 50)"],
    date: Annotated[str, "Data nel formato yyyy-MM-dd"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni metriche storiche per uno o più domini in una data specifica."""
    return _fmt(await client.domain_metrics_history(domains, date, db))


@mcp.tool()
async def domain_authority(
    domains: Annotated[list[str], "Lista di domini (max 100)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni Zoom Authority, Trust, Stability e Opportunity per uno o più domini."""
    return _fmt(await client.domain_authority(domains, db))


@mcp.tool()
async def domain_niches(
    domains: Annotated[list[str], "Lista di domini (max 10)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di nicchie per dominio"] = None,
) -> str:
    """Ottieni le nicchie tematiche di uno o più domini con topical authority e percentuale keyword."""
    return _fmt(await client.domain_niches(domains, db, limit))


@mcp.tool()
async def domain_best_pages(
    domain: Annotated[str, "Singolo dominio"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di pagine"] = None,
) -> str:
    """Ottieni le pagine migliori di un dominio con PZA e keyword totali posizionate."""
    return _fmt(await client.domain_best_pages(domain, db, limit))


@mcp.tool()
async def domain_ai_keywords(
    domain: Annotated[str, "Singolo dominio"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    offset: Annotated[int | None, "Posizione di partenza dei risultati"] = None,
    limit: Annotated[int | None, "Numero massimo di keyword"] = None,
) -> str:
    """Ottieni le keyword per cui il dominio appare nelle AI Overview di Google."""
    return _fmt(await client.domain_ai_keywords(domain, db, offset, limit))


@mcp.tool()
async def domain_keywords(
    domain: Annotated[str, "Singolo dominio"],
    type: Annotated[str, "Tipo filtro: best, withtraffic, up, down, stable, entered, exited, bypage, byposition, newentry"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    offset: Annotated[int | None, "Posizione di partenza dei risultati"] = None,
    limit: Annotated[int | None, "Numero massimo di keyword"] = None,
) -> str:
    """Ottieni le keyword posizionate di un dominio filtrate per tipo (best, up, down, etc.)."""
    return _fmt(await client.domain_keywords(domain, type, db, offset, limit))


@mcp.tool()
async def domain_competitors(
    domains: Annotated[list[str], "Lista di domini (max 10)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di competitor per dominio"] = None,
) -> str:
    """Ottieni i principali competitor organici di uno o più domini."""
    return _fmt(await client.domain_competitors(domains, db, limit))


# ── URLs ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def url_page_authority(
    url: Annotated[str, "Singola URL completa"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni il Page Zoom Authority (PZA) di una singola URL."""
    return _fmt(await client.url_page_authority(url, db))


@mcp.tool()
async def url_metrics(
    urls: Annotated[list[str], "Lista di URL (max 30)"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni metriche dettagliate per una o più URL: keyword totali, traffico, PZA."""
    return _fmt(await client.url_metrics(urls, db))


@mcp.tool()
async def url_keywords(
    url: Annotated[str, "Singola URL completa"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di keyword"] = None,
) -> str:
    """Ottieni le keyword per cui una URL è posizionata con volumi, posizioni e CPC."""
    return _fmt(await client.url_keywords(url, db, limit))


@mcp.tool()
async def url_intent_gap(
    url: Annotated[str, "Singola URL completa"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di risultati"] = None,
) -> str:
    """Ottieni il gap di intent: keyword con potenziale non sfruttato per una URL."""
    return _fmt(await client.url_intent_gap(url, db, limit))


# ── Projects ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def project_list(
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni la lista di tutti i progetti SEOZoom con metriche principali."""
    return _fmt(await client.project_list(db))


@mcp.tool()
async def project_overview(
    id: Annotated[str, "ID del progetto"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni la panoramica completa di un progetto: keyword monitorate, traffico, ZA, trust."""
    return _fmt(await client.project_overview(id, db))


@mcp.tool()
async def project_keywords(
    id: Annotated[str, "ID del progetto"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
) -> str:
    """Ottieni le keyword monitorate di un progetto con volumi, posizioni e traffico stimato."""
    return _fmt(await client.project_keywords(id, db))


@mcp.tool()
async def project_best_pages(
    id: Annotated[str, "ID del progetto"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di pagine"] = None,
) -> str:
    """Ottieni le migliori pagine di un progetto con PZA e keyword totali."""
    return _fmt(await client.project_best_pages(id, db, limit))


@mcp.tool()
async def project_pages_with_more_keywords(
    id: Annotated[str, "ID del progetto"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di pagine"] = None,
) -> str:
    """Ottieni le pagine del progetto con il maggior numero di keyword posizionate."""
    return _fmt(await client.project_pages_with_more_keywords(id, db, limit))


@mcp.tool()
async def project_pages_with_potential(
    id: Annotated[str, "ID del progetto"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di pagine"] = None,
) -> str:
    """Ottieni le pagine del progetto con maggiore potenziale di crescita traffico."""
    return _fmt(await client.project_pages_with_potential(id, db, limit))


@mcp.tool()
async def project_winner_pages(
    id: Annotated[str, "ID del progetto"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di pagine"] = None,
) -> str:
    """Ottieni le pagine del progetto in crescita (variazione traffico positiva)."""
    return _fmt(await client.project_winner_pages(id, db, limit))


@mcp.tool()
async def project_loser_pages(
    id: Annotated[str, "ID del progetto"],
    db: Annotated[str | None, "Database paese (it, es, fr, de, uk)"] = None,
    limit: Annotated[int | None, "Numero massimo di pagine"] = None,
) -> str:
    """Ottieni le pagine del progetto in calo (variazione traffico negativa)."""
    return _fmt(await client.project_loser_pages(id, db, limit))


# ── Utility ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def check_units() -> str:
    """Controlla le unità API rimanenti (costa 10 unit)."""
    data = await client.keyword_metrics(["test"])
    remaining = data.get("UnitsRemaining", "?")
    return f"Unità API rimanenti: {remaining}"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
