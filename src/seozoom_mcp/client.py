from __future__ import annotations

import os
from typing import Any

import httpx

BASE_URL = "https://apiv2.seozoom.com/api/v2"


class SEOZoomError(Exception):
    pass


VALID_DBS = {"it", "es", "fr", "de", "uk"}


class SEOZoomClient:
    def __init__(self) -> None:
        api_key = os.environ.get("SEOZOOM_API_KEY")
        if not api_key:
            raise SEOZoomError("SEOZOOM_API_KEY environment variable is required")
        self._api_key = api_key
        self._default_db = os.environ.get("SEOZOOM_DEFAULT_DB", "it")
        self._http = httpx.AsyncClient(timeout=30)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _db(self, db: str | None) -> str:
        val = db or self._default_db
        if val not in VALID_DBS:
            raise SEOZoomError(f"Database '{val}' non valido. Usa: {', '.join(sorted(VALID_DBS))}")
        return val

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        params["api_key"] = self._api_key
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

    async def keyword_metrics(self, keywords: list[str], db: str | None = None) -> Any:
        return await self._get("keywords", {
            "action": "metrics",
            "db": self._db(db),
            "keyword": "|".join(keywords),
        })

    async def keyword_serp(self, keywords: list[str], db: str | None = None) -> Any:
        return await self._get("keywords", {
            "action": "serp",
            "db": self._db(db),
            "keyword": "|".join(keywords),
        })

    async def keyword_serp_history(self, keyword: str, date: str, db: str | None = None) -> Any:
        return await self._get("keywords", {
            "action": "serphistory",
            "db": self._db(db),
            "keyword": keyword,
            "date": date,
        })

    async def keyword_related(self, keyword: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("keywords", {
            "action": "related",
            "db": self._db(db),
            "keyword": keyword,
            "limit": limit if limit is not None else 50,
        })

    # ── Domains ──────────────────────────────────────────────

    async def domain_metrics(self, domains: list[str], db: str | None = None) -> Any:
        return await self._get("domains", {
            "action": "metrics",
            "db": self._db(db),
            "domain": "|".join(domains),
        })

    async def domain_metrics_history(self, domains: list[str], date: str, db: str | None = None) -> Any:
        return await self._get("domains", {
            "action": "metricshistory",
            "db": self._db(db),
            "domain": "|".join(domains),
            "date": date,
        })

    async def domain_authority(self, domains: list[str], db: str | None = None) -> Any:
        return await self._get("domains", {
            "action": "authority",
            "db": self._db(db),
            "domain": "|".join(domains),
        })

    async def domain_niches(self, domains: list[str], db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("domains", {
            "action": "niches",
            "db": self._db(db),
            "domain": "|".join(domains),
            "limit": limit if limit is not None else 10,
        })

    async def domain_best_pages(self, domain: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("domains", {
            "action": "bestpages",
            "db": self._db(db),
            "domain": domain,
            "limit": limit,
        })

    async def domain_ai_keywords(self, domain: str, db: str | None = None, offset: int | None = None, limit: int | None = None) -> Any:
        return await self._get("domains", {
            "action": "aikeywords",
            "db": self._db(db),
            "domain": domain,
            "offset": offset,
            "limit": limit,
        })

    async def domain_keywords(self, domain: str, type: str, db: str | None = None, offset: int | None = None, limit: int | None = None) -> Any:
        return await self._get("domains", {
            "action": "keywords",
            "db": self._db(db),
            "domain": domain,
            "type": type,
            "offset": offset,
            "limit": limit,
        })

    async def domain_competitors(self, domains: list[str], db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("domains", {
            "action": "competitor",
            "db": self._db(db),
            "domain": "|".join(domains),
            "limit": limit,
        })

    # ── URLs ─────────────────────────────────────────────────

    async def url_page_authority(self, url: str, db: str | None = None) -> Any:
        return await self._get("urls", {
            "action": "urlpza",
            "db": self._db(db),
            "url": url,
        })

    async def url_metrics(self, urls: list[str], db: str | None = None) -> Any:
        return await self._get("urls", {
            "action": "metrics",
            "db": self._db(db),
            "url": "|".join(urls),
        })

    async def url_keywords(self, url: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("urls", {
            "action": "keywords",
            "db": self._db(db),
            "url": url,
            "limit": limit,
        })

    async def url_intent_gap(self, url: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("urls", {
            "action": "intentgap",
            "db": self._db(db),
            "url": url,
            "limit": limit,
        })

    # ── Projects ─────────────────────────────────────────────

    async def project_list(self, db: str | None = None) -> Any:
        return await self._get("projects", {
            "action": "list",
            "db": self._db(db),
        })

    async def project_overview(self, id: str, db: str | None = None) -> Any:
        return await self._get("projects", {
            "action": "overview",
            "db": self._db(db),
            "id": id,
        })

    async def project_keywords(self, id: str, db: str | None = None) -> Any:
        return await self._get("projects", {
            "action": "keywords",
            "db": self._db(db),
            "id": id,
        })

    async def project_best_pages(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("projects", {
            "action": "bestpages",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })

    async def project_pages_with_more_keywords(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("projects", {
            "action": "pageswithmorekeywords",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })

    async def project_pages_with_potential(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("projects", {
            "action": "pageswithpotential",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })

    async def project_winner_pages(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("projects", {
            "action": "winnerpages",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })

    async def project_loser_pages(self, id: str, db: str | None = None, limit: int | None = None) -> Any:
        return await self._get("projects", {
            "action": "loserpages",
            "db": self._db(db),
            "id": id,
            "limit": limit,
        })
