"""Leitura de User Stories do Jira Cloud (API REST v3).

A descrição das User Stories está em ADF (Atlassian Document Format), uma árvore JSON.
Este módulo converte-a em texto simples estruturado (títulos, listas numeradas), que é
o que o Agente Analista recebe.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

HTTP_TIMEOUT_S = 15.0


class JiraReadError(Exception):
    pass


@dataclass(frozen=True)
class JiraStory:
    key: str
    summary: str
    description: str
    labels: tuple[str, ...]

    def as_text(self) -> str:
        """Texto completo da User Story (usado no prompt e na pesquisa RAG)."""
        return f"{self.key} — {self.summary}\n\n{self.description}"


def adf_to_text(node: dict[str, Any]) -> str:
    """Converte um documento ADF em texto: títulos com '## ', listas com '1.' / '-'."""
    lines: list[str] = []

    def inline(n: dict[str, Any]) -> str:
        if n.get("type") == "text":
            return str(n.get("text", ""))
        if n.get("type") == "hardBreak":
            return "\n"
        return "".join(inline(c) for c in n.get("content", []))

    def block(n: dict[str, Any], prefix: str = "") -> None:
        kind = n.get("type")
        if kind == "heading":
            lines.append("")
            lines.append("## " + inline(n).strip())
        elif kind == "paragraph":
            text = inline(n).strip()
            if text:
                lines.append(prefix + text)
        elif kind == "orderedList":
            for i, item in enumerate(n.get("content", []), start=1):
                for child in item.get("content", []):
                    block(child, prefix=f"{i}. ")
        elif kind == "bulletList":
            for item in n.get("content", []):
                for child in item.get("content", []):
                    block(child, prefix="- ")
        else:
            for child in n.get("content", []):
                block(child, prefix)

    block(node)
    return "\n".join(lines).strip()


def fetch_story(http: requests.Session, base_url: str, auth: tuple[str, str], key: str) -> JiraStory:
    res = http.get(
        f"{base_url.rstrip('/')}/rest/api/3/issue/{key}",
        params={"fields": "summary,description,labels,issuetype"},
        auth=auth,
        timeout=HTTP_TIMEOUT_S,
    )
    if res.status_code == 404:
        raise JiraReadError(f"{key} não existe ou sem permissão de leitura")
    if not res.ok:
        raise JiraReadError(f"{key}: HTTP {res.status_code} — {res.text[:200]}")

    fields: dict[str, Any] = res.json()["fields"]
    if fields.get("issuetype", {}).get("name") != "Story":
        raise JiraReadError(f"{key} não é uma Story (tipo: {fields.get('issuetype', {}).get('name')})")
    description = fields.get("description")
    if not description:
        raise JiraReadError(f"{key} não tem descrição")

    return JiraStory(
        key=key,
        summary=str(fields["summary"]),
        description=adf_to_text(description),
        labels=tuple(fields.get("labels", [])),
    )
