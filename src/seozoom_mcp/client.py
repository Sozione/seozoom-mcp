"""Client asincrono per le API SEOZoom v2.

Gestisce autenticazione, validazione del database e tutte le chiamate
HTTP verso i 4 endpoint principali: keywords, domains, urls, projects.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

# URL base delle API SEOZoom v2 — tutti gli endpoint partono da qui
BASE_URL = "https://apiv2.seozoom.com/api/v2"


class SEOZoomError(Exception):
    """Eccezione sollevata per errori API SEOZoom (autenticazione, HTTP, validazione)."""


# Database supportati: Italia, Spagna, Francia, Germania, Regno Unito
VALID_DBS = {"it", "es", "fr", "de", "uk"}


class SEOZoomClient:
    """Client asincrono per le API SEOZoom v2.

    Legge la chiave API dalla variabile d'ambiente SEOZOOM_API_KEY
    e il database di default da SEOZOOM_DEFAULT_DB (fallback: "it").
    Utilizza httpx.AsyncClient per le richieste HTTP con timeout di 30s.
    """

    def __init__(self) -> None:
        api_key = os.environ.get("SEOZOOM_API_KEY")
        if not api_key:
            raise SEOZoomError("SEOZOOM_API_KEY environment variable is required")
        self._api_key = api_key
        self._default_db = os.environ.get("SEOZOOM_DEFAULT_DB", "it")
        self._http = httpx.AsyncClient(timeout=30)

    async def aclose(self) -> None:
        """Chiude il client HTTP. Da chiamare al termine dell'uso."""
        await self._http.aclose()

    def _db(self, db: str | None) -> str:
        """Risolve il database: usa quello passato o il default, validandolo."""
        val = db or self._default_db
        if val not in VALID_DBS:
            raise SEOZoomError(f"Database '{val}' non valido. Usa: {', '.join(sorted(VALID_DBS))}")
        return val

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        """Esegue una richiesta GET autenticata alle API SEOZoom.

        Aggiunge automaticamente la api_key, rimuove i parametri None
        e solleva SEOZoomError in caso di errore HTTP.
        """
        params["api_key"] = self._api_key
        # Rimuove i parametri opzionali non forniti
        params = {k: v for k, v in params.items() if v is not None}
        resp = await self._http.get(f"{BASE_URL}/{path}/", params=params)
        if resp.status_code >= 400:
            try:
                msg = resp.json().get("message", f"HTTP {resp.status_code}")
            except Exception:
                msg = f"HTTP {resp.status_code}"
            raise SEOZoomError(msg)
        return resp.json()

    # ── Keywords ─────────────────────────────────────────────
    # Endpoint per analisi keyword: metriche, SERP, storico e correlate.
    # Le keyword multiple vengono separate da "|" nel parametro query.

    async def keyword_metrics(self, keywords: list[str], db: str | None = None) -> Any:
        """Metriche keyword: volume di ricerca, KD, CPC, intent e trend mensili."""
        return await self._get("keywords", {
            "action": "metrics",
            "db": self._db(db),
            "keyword": "|".join(keywords),
        })

    async def keyword_serp(self, keywords: list[str], db: str | None = None) -> Any:
        """Risultati SERP attuali (fino a 50 risultati organici) per le keyword."""
        return await self._get("keywords", {
            "action": "serp",
            "db": self._db(db),
            "keyword": "|".join(keywords),
        })

    async def keyword_serp_history(self, keyword: str, date: str, db: str | None = None) -> Any:
        """Snapshot storico della SERP per una keyword in una data specifica."""
        return await self._get("keywords", {
            "action": "serphistory",
            "db": self._db(db),
            "keyword": keyword,
            "date": date,
        })

    async def keyword_related(self, keyword: str, db: str | None = None, limit: int | None = None) -> Any:
        """Keyword correlate con volume e affinità SERP (default: 50 risultati)."""
        return await self._get("keywords", {
            "action": "related",
            "db": self._db(db),
            "keyword": keyword,
            "limit": limit if limit is not None else 50,
        })

    # ── Domains ──────────────────────────────────────────────
    # Endpoint per analisi domini: metriche, authority, nicchie, pagine e competitor.
    # I domini multipli vengono separati da "|" nel parametro query.

    async def domain_metrics(self, domains: list[str], db: str | None = None) -> Any:
        """Metriche dominio: traffico stimato, keyword posizionate, ZA."""
        return await self._get("domains", {
            "action": "metrics",
            "db": self._db(db),
            "domain": "|".join(domains),
        })

    async def domain_metrics_history(self, domains: list[str], date: str, db: str | None = None) -> Any:
        """Metriche storiche di uno o più domini in una data specifica."""
        return await self._get("domains", {
            "action": "metricshistory",
            "db": self._db(db),
            "domain": "|".join(domains),
            "date": date,
        })

    async def domain_authority(self, domains: list[str], db: str | None = None) -> Any:
        """Zoom Authority, Trust, Stability e Opportunity per i domini."""
        return await self._get("domains", {
            "action": "authority",
            "db": self._db(db),
            "domain": "|".join(domains),
        })

    async def domain_niches(self, domains: list[str], db: str | None = None, limit: int | None = None) -> Any:
        """Nicchie tematiche con topical authority e % keyword (default: 10)."""
        return await self._get("domains", {
            "action": "niches",
            "db": self._db(db),
            "domain": "|".join(domains),
            "limit": limit if limit is not None else 10,
        })

    async def domain_best_pages(self, domain: str, db: str | None = None, limit: int | None = None) -> Any:
        """Pagine migliori di un dominio con PZA e keyword totali."""
        return await self._get("domains", {
            "action": "bestpages",
            "db": self._db(db),
            "domain": domain,
            "limit": limit,
        })

    async def domain_ai_keywords(self, domain: str, db: str | None = None, offset: int | None = None, limit: int | None = None) -> Any:
        """Keyword per cui il dominio appare nelle AI Overview di Google."""
        return await self._get("domains", {
            "action": "aikeywords",
            "db": self._db(db),
            "domain": domain,
            "offset": offset,
            "limit": limit,
        })

    async def domain_keywords(self, domain: str, type: str, db: str | None = None, offset: int | None = None, limit: int | None = None) -> Any:
        """Keyword posizionate filtrate per tipo (best, up, down, stable, entered, exited, ecc.)."""
        return await self._get("domains", {
            "action": "keywords",
            "db": self._db(db),
            "domain": domain,
            "type": type,
            "offset": offset,
            "limit": limit,
        })

    async def domain_competitors(self, domains: list[str], db: str | None = None, limit: int | None = None) -> Any:
        """Principali competitor organici di uno o più domini."""
        return await self._get("domains", {
            "action": "competitor",
            "db": self._db(db),
            "domain": "|".join(domains),
            "limit": limit,
        })

    # ── URLs ─────────────────────────────────────────────────
    # Endpoint per analisi URL: authority, metriche, keyword posizionate e intent gap.
    # Le URL multiple vengono separate da "|" nel parametro query.

    async def url_page_authority(self, url: str, db: str | None = None) -> Any:
        """Page Zoom Authority (PZA) di una singola URL."""
        return await self._get("urls", {
            "action": "urlpza",
            "db": self._db(db),
            "url": url,
        })

    async def url_metrics(self, urls: list[str], db: str | None = None) -> Any:
        """Metriche dettagliate per URL: keyword totali, traffico, PZA."""
        return await self._get("urls", {
            "action": "metrics",
            "db": self._db(db),
            "url": "|".join(urls),
        })

    async def url_keywords(self, url: str, db: str | None = None, limit: int | None = None) -> Any:
        """Keyword per cui una URL è posizionata con volumi, posizioni e CPC."""
        return await self._get("urls", {
            "action": "keywords",
            "db": self._db(db),
            "url": url,
            "limit": limit,
        })

    async def url_intent_gap(self, url: str, db: str | None = None, limit: int | None = None) -> Any:
        """Intent gap: keyword con potenziale non sfruttato per una URL."""
        return await self._get("urls", {
            "action": "intentgap",
            "db": self._db(db),
            "url": url,
            "limit": limit,
        })

    # ── Projects ─────────────────────────────────────────────
    # Endpoint per gestione progetti SEOZoom: lista, overview, keyword e pagine.
    # Ogni progetto è identificato dal suo ID univoco.

    async def project_list(self, db: str | None = None) -> Any:
        """Lista di tutti i progetti con metriche principali."""
        return await self._get("projects", {
            "action": "list",
            "db": self._db(db),
        })

    async def project_overview(self, id: str, db: str | None = None) -> Any:
        """Panoramica completa di un progetto: keyword, traffico, ZA, trust."""
        return await self._get("projects", {
            "action": "overview",
            "db": self._db(db),
            "id": id,
        })

    async def project_keywords(self, id: str, db: str | None = None) -> Any:
        """Keyword monitorate del progetto con volumi, posizioni e traffico."""
        return await self._get("projects", {
            "action": "keywords",
            "db": self._db(db),
            "id": id,
        })

    async def project_best_pages(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        """Migliori pagine del progetto con PZA e keyword totali."""
        return await self._get("projects", {
            "action": "bestpages",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })

    async def project_pages_with_more_keywords(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        """Pagine del progetto con il maggior numero di keyword posizionate."""
        return await self._get("projects", {
            "action": "pageswithmorekeywords",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })

    async def project_pages_with_potential(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        """Pagine del progetto con maggiore potenziale di crescita traffico."""
        return await self._get("projects", {
            "action": "pageswithpotential",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })

    async def project_winner_pages(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        """Pagine del progetto in crescita (variazione traffico positiva)."""
        return await self._get("projects", {
            "action": "winnerpages",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })

    async def project_loser_pages(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        """Pagine del progetto in calo (variazione traffico negativa)."""
        return await self._get("projects", {
            "action": "loserpages",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })
