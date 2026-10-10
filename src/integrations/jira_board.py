"""Movimento automático da User Story pelas colunas do quadro Kanban do Jira.

As colunas espelham as etapas do fluxo (subcapítulo 6.4.3):
    Backlog → AI Generating Tests → In Review → Automated Execution → Done

O movimento é feito pela API REST v3 (transições do workflow). Uma falha aqui nunca
interrompe o fluxo principal: é apenas reportada como aviso.
"""

from __future__ import annotations

import os

import requests

HTTP_TIMEOUT_S = 30

BACKLOG = "Backlog"
GENERATING = "AI Generating Tests"
IN_REVIEW = "In Review"
EXECUTING = "Automated Execution"
DONE = "Done"


class BoardError(Exception):
    """Não foi possível mover a User Story (estado inexistente, sem permissão, etc.)."""


def move_story(http: requests.Session, root: str, auth: tuple[str, str], key: str, status: str) -> str:
    """Move `key` para a coluna/estado `status`. Devolve uma descrição curta do que aconteceu."""
    base = f"{root.rstrip('/')}/rest/api/3/issue/{key}"
    r = http.get(base, auth=auth, params={"fields": "status"}, timeout=HTTP_TIMEOUT_S)
    if not r.ok:
        raise BoardError(f"{key}: HTTP {r.status_code} ao ler o estado")
    current = r.json()["fields"]["status"]["name"]
    if current.lower() == status.lower():
        return f"{key} já está em {status}"

    r = http.get(f"{base}/transitions", auth=auth, timeout=HTTP_TIMEOUT_S)
    if not r.ok:
        raise BoardError(f"{key}: HTTP {r.status_code} ao ler as transições")
    transitions = r.json().get("transitions", [])
    match = next((t for t in transitions if t["to"]["name"].lower() == status.lower()), None)
    if match is None:
        available = ", ".join(sorted({t["to"]["name"] for t in transitions})) or "nenhuma"
        raise BoardError(f"{key}: sem transição de '{current}' para '{status}' (disponíveis: {available})")

    r = http.post(f"{base}/transitions", auth=auth, json={"transition": {"id": match["id"]}}, timeout=HTTP_TIMEOUT_S)
    if not r.ok:
        raise BoardError(f"{key}: HTTP {r.status_code} ao mudar para {status} — {r.text[:200]}")
    return f"{key}: {current} → {status}"


def try_move(http: requests.Session, root: str, auth: tuple[str, str], key: str, status: str) -> None:
    """Versão tolerante: imprime o resultado e nunca lança exceção."""
    try:
        print(f"  📋 quadro: {move_story(http, root, auth, key, status)}")
    except (BoardError, requests.RequestException) as exc:
        print(f"  ⚠️  quadro: não foi possível mover ({exc})")


def credentials_from_env() -> tuple[str, tuple[str, str]] | None:
    """(URL base, (email, token)) a partir do ambiente, ou None se faltar alguma variável."""
    root = os.getenv("ATLASSIAN_BASE_URL")
    email = os.getenv("ATLASSIAN_USER_EMAIL")
    token = os.getenv("ATLASSIAN_API_TOKEN")
    if not (root and email and token):
        return None
    return root, (email, token)
