"""Leitura da base de conhecimento a partir do Confluence Cloud (API REST v2)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

HTTP_TIMEOUT_S = 15.0


class ConfluenceSourceError(Exception):
    pass


@dataclass(frozen=True)
class KnowledgePage:
    page_id: str
    title: str
    version: int
    storage_xhtml: str
    web_url: str


def _get(http: requests.Session, url: str, auth: tuple[str, str], params: dict[str, Any], context: str) -> dict[str, Any]:
    res = http.get(url, params=params, auth=auth, timeout=HTTP_TIMEOUT_S)
    if not res.ok:
        raise ConfluenceSourceError(f"{context}: HTTP {res.status_code} — {res.text[:200]}")
    return res.json()


def fetch_page(
    http: requests.Session,
    base_url: str,
    auth: tuple[str, str],
    space_key: str,
    title: str,
) -> KnowledgePage:
    """Obtém a versão atual da página (corpo em Storage Format) pelo título e espaço."""
    root = base_url.rstrip("/")
    spaces = _get(http, f"{root}/wiki/api/v2/spaces", auth, {"keys": space_key, "limit": 1}, "obter espaço")
    if not spaces.get("results"):
        raise ConfluenceSourceError(f"espaço '{space_key}' não encontrado")
    space_id = spaces["results"][0]["id"]

    pages = _get(
        http,
        f"{root}/wiki/api/v2/pages",
        auth,
        {"space-id": space_id, "title": title, "status": "current", "limit": 1},
        "procurar página",
    )
    if not pages.get("results"):
        raise ConfluenceSourceError(f"página '{title}' não encontrada no espaço '{space_key}'")
    page_id = str(pages["results"][0]["id"])

    page = _get(http, f"{root}/wiki/api/v2/pages/{page_id}", auth, {"body-format": "storage"}, "obter conteúdo")
    body = page.get("body", {}).get("storage", {}).get("value")
    if not body:
        raise ConfluenceSourceError("a página não tem conteúdo em Storage Format")

    return KnowledgePage(
        page_id=page_id,
        title=page["title"],
        version=int(page["version"]["number"]),
        storage_xhtml=body,
        web_url=f"{root}/wiki/pages/viewpage.action?pageId={page_id}",
    )
