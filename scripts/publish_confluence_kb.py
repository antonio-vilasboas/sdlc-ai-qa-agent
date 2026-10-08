"""Publica a base de conhecimento do Swag Labs no Confluence Cloud.

Fonte: knowledge/swaglabs_knowledge_base.md (versionado no Git, revisto pelo autor).
Destino: página com o título do H1 no espaço CONFLUENCE_SPACE_KEY.

A conversão Markdown → Confluence Storage Format (XHTML) preserva títulos H2, tabelas,
listas e código inline. Cada H2 é uma secção autocontida: é a unidade de divisão
(chunk) usada mais tarde na indexação vetorial (RAG).

Operação idempotente: cria a página se não existir; caso contrário, publica uma nova
versão (o histórico de versões do Confluence regista cada alteração).

Uso:
    python scripts/publish_confluence_kb.py             # publicar / atualizar
    python scripts/publish_confluence_kb.py --dry-run   # só gerar o XHTML
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import markdown
import requests
from pydantic import ValidationError

from sanity_check import HTTP_TIMEOUT_S, Settings, build_session, load_settings

KB_FILE = Path(__file__).resolve().parent.parent / "knowledge" / "swaglabs_knowledge_base.md"
DRY_RUN_OUT = KB_FILE.with_suffix(".storage.html")


class ConfluenceError(Exception):
    pass


# --------------------------------------------------------------------------- #
# Conversão
# --------------------------------------------------------------------------- #
def split_title(md_text: str) -> tuple[str, str]:
    """Separa o H1 (título da página) do corpo."""
    lines = md_text.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("o ficheiro tem de começar por um título H1 ('# <título>')")
    return lines[0][2:].strip(), "\n".join(lines[1:]).strip()


def to_storage(md_body: str) -> str:
    """Markdown → XHTML aceite pelo Confluence Storage Format."""
    html = markdown.markdown(md_body, extensions=["tables", "sane_lists"], output_format="xhtml")
    if not html.strip():
        raise ValueError("conteúdo vazio após conversão")
    return html


# --------------------------------------------------------------------------- #
# Cliente Confluence (API v2)
# --------------------------------------------------------------------------- #
def _check(res: requests.Response, context: str) -> dict[str, Any]:
    if not res.ok:
        raise ConfluenceError(f"{context}: HTTP {res.status_code} — {res.text[:300]}")
    return res.json()


def get_space_id(cfg: Settings, http: requests.Session) -> str:
    data = _check(
        http.get(
            f"{cfg.atlassian_root}/wiki/api/v2/spaces",
            params={"keys": cfg.confluence_space_key, "limit": 1},
            auth=cfg.atlassian_auth,
            timeout=HTTP_TIMEOUT_S,
        ),
        "obter espaço",
    )
    results: list[dict[str, Any]] = data.get("results", [])
    if not results:
        raise ConfluenceError(f"espaço '{cfg.confluence_space_key}' não encontrado")
    return str(results[0]["id"])


def find_page(cfg: Settings, http: requests.Session, space_id: str, title: str) -> dict[str, Any] | None:
    data = _check(
        http.get(
            f"{cfg.atlassian_root}/wiki/api/v2/pages",
            params={"space-id": space_id, "title": title, "status": "current", "limit": 1},
            auth=cfg.atlassian_auth,
            timeout=HTTP_TIMEOUT_S,
        ),
        "procurar página",
    )
    results: list[dict[str, Any]] = data.get("results", [])
    return results[0] if results else None


def upsert_page(cfg: Settings, http: requests.Session, title: str, storage: str) -> tuple[str, int, str]:
    """Devolve (page_id, versão, ação)."""
    space_id = get_space_id(cfg, http)
    body = {"representation": "storage", "value": storage}
    existing = find_page(cfg, http, space_id, title)

    if existing is None:
        data = _check(
            http.post(
                f"{cfg.atlassian_root}/wiki/api/v2/pages",
                json={"spaceId": space_id, "status": "current", "title": title, "body": body},
                auth=cfg.atlassian_auth,
                timeout=HTTP_TIMEOUT_S,
            ),
            "criar página",
        )
        return str(data["id"]), int(data["version"]["number"]), "criada"

    page_id = str(existing["id"])
    next_version = int(existing["version"]["number"]) + 1
    data = _check(
        http.put(
            f"{cfg.atlassian_root}/wiki/api/v2/pages/{page_id}",
            json={
                "id": page_id,
                "status": "current",
                "title": title,
                "body": body,
                "version": {"number": next_version, "message": "Atualização via publish_confluence_kb.py"},
            },
            auth=cfg.atlassian_auth,
            timeout=HTTP_TIMEOUT_S,
        ),
        "atualizar página",
    )
    return page_id, int(data["version"]["number"]), "atualizada"


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publica a base de conhecimento no Confluence.")
    parser.add_argument("--dry-run", action="store_true", help="gera o XHTML localmente sem chamar a API")
    args = parser.parse_args(argv)

    try:
        title, md_body = split_title(KB_FILE.read_text(encoding="utf-8"))
        storage = to_storage(md_body)
    except (OSError, ValueError) as exc:
        print(f"❌ {KB_FILE.name}: {exc}")
        return 1

    n_sections = storage.count("<h2>")
    if args.dry_run:
        DRY_RUN_OUT.write_text(storage, encoding="utf-8")
        print(f"✅ '{title}': {n_sections} secções, {len(storage)} caracteres → {DRY_RUN_OUT.name}")
        return 0

    try:
        cfg = load_settings()
    except ValidationError as exc:
        print(f"❌ .env inválido: {exc}")
        return 1

    print(f"→ A publicar '{title}' ({n_sections} secções) no espaço {cfg.confluence_space_key}")
    try:
        page_id, version, action = upsert_page(cfg, build_session(), title, storage)
    except (ConfluenceError, requests.RequestException) as exc:
        print(f"❌ {exc}")
        return 1

    print(f"✅ Página {action} (id {page_id}, versão {version})")
    print(f"   {cfg.atlassian_root}/wiki/pages/viewpage.action?pageId={page_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
