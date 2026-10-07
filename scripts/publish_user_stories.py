"""Publica no Jira Cloud as User Stories definidas em requirements/user_stories.json.

As stories são versionadas no repositório (requirements as code) e publicadas com a
descrição em Atlassian Document Format (ADF), para que títulos e listas fiquem
estruturados — condição para o Agente Analista extrair os critérios de aceitação.

Operação idempotente, uma story por execução:
  - se já existir no projeto uma issue com a label do id (ex.: "us-01"), é atualizada;
  - se for indicado --key, essa issue é atualizada (útil para stories criadas à mão);
  - caso contrário, é criada.

Uso:
    python scripts/publish_user_stories.py --story 1 --key QAAGENT-1   # atualizar a já existente
    python scripts/publish_user_stories.py --story 2                   # criar a seguinte
    python scripts/publish_user_stories.py --story 3 --dry-run         # só mostrar o payload
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Literal

import requests
from pydantic import BaseModel, Field, ValidationError

from sanity_check import HTTP_TIMEOUT_S, Settings, build_session, load_settings

STORIES_FILE = Path(__file__).resolve().parent.parent / "requirements" / "user_stories.json"
ISSUE_TYPE = "Story"

AdfNode = dict[str, Any]


# --------------------------------------------------------------------------- #
# Modelo dos requisitos
# --------------------------------------------------------------------------- #
class StoryNarrative(BaseModel):
    como: str = Field(min_length=3)
    quero: str = Field(min_length=3)
    para: str = Field(min_length=3)


class UserStory(BaseModel):
    id: str = Field(pattern=r"^us-\d{2}$")
    summary: str = Field(min_length=5, max_length=255)
    priority: Literal["Highest", "High", "Medium", "Low", "Lowest"]
    labels: list[str] = Field(min_length=1)
    story: StoryNarrative
    context: str
    acceptance_criteria: list[str] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)

    @property
    def all_labels(self) -> list[str]:
        """Labels declaradas + label de identificação estável (us-NN)."""
        return sorted({*self.labels, self.id})


def load_stories(path: Path = STORIES_FILE) -> list[UserStory]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [UserStory.model_validate(item) for item in raw]


# --------------------------------------------------------------------------- #
# Construção de ADF (Atlassian Document Format)
# --------------------------------------------------------------------------- #
def _text(value: str, bold: bool = False) -> AdfNode:
    node: AdfNode = {"type": "text", "text": value}
    if bold:
        node["marks"] = [{"type": "strong"}]
    return node


def _heading(value: str, level: int = 2) -> AdfNode:
    return {"type": "heading", "attrs": {"level": level}, "content": [_text(value)]}


def _paragraph(*content: AdfNode) -> AdfNode:
    return {"type": "paragraph", "content": list(content)}


def _list(items: list[str], ordered: bool) -> AdfNode:
    return {
        "type": "orderedList" if ordered else "bulletList",
        "content": [{"type": "listItem", "content": [_paragraph(_text(i))]} for i in items],
    }


def build_description(us: UserStory) -> AdfNode:
    hard_break: AdfNode = {"type": "hardBreak"}
    content: list[AdfNode] = [
        _heading("História de Utilizador"),
        _paragraph(
            _text("Como ", bold=True), _text(us.story.como + ","), hard_break,
            _text("quero ", bold=True), _text(us.story.quero + ","), hard_break,
            _text("para ", bold=True), _text(us.story.para + "."),
        ),
        _heading("Contexto"),
        _paragraph(_text(us.context)),
        _heading("Critérios de Aceitação"),
        _list(us.acceptance_criteria, ordered=True),
    ]
    if us.notes:
        content += [_heading("Notas"), _list(us.notes, ordered=False)]
    return {"type": "doc", "version": 1, "content": content}


def build_fields(us: UserStory, project_key: str, *, include_priority: bool, for_create: bool) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "summary": us.summary,
        "description": build_description(us),
        "labels": us.all_labels,
    }
    if for_create:
        fields["project"] = {"key": project_key}
        fields["issuetype"] = {"name": ISSUE_TYPE}
    if include_priority:
        fields["priority"] = {"name": us.priority}
    return fields


# --------------------------------------------------------------------------- #
# Cliente Jira (mínimo, só o necessário para este script)
# --------------------------------------------------------------------------- #
class JiraError(Exception):
    pass


def _raise_for(res: requests.Response, context: str) -> None:
    if not res.ok:
        raise JiraError(f"{context}: HTTP {res.status_code} — {res.text[:300]}")


def _priority_rejected(res: requests.Response) -> bool:
    """Projetos team-managed podem não ter o campo Priority no ecrã."""
    return res.status_code == 400 and "priority" in res.text.lower()


def find_by_label(cfg: Settings, http: requests.Session, label: str) -> str | None:
    res = http.get(
        f"{cfg.atlassian_root}/rest/api/3/search/jql",
        params={"jql": f'project = "{cfg.jira_project_key}" AND labels = "{label}"', "fields": "summary", "maxResults": 2},
        auth=cfg.atlassian_auth,
        timeout=HTTP_TIMEOUT_S,
    )
    _raise_for(res, f"pesquisa JQL pela label '{label}'")
    issues: list[dict[str, Any]] = res.json().get("issues", [])
    if len(issues) > 1:
        raise JiraError(f"mais do que uma issue com a label '{label}' — resolve manualmente antes de continuar")
    return issues[0]["key"] if issues else None


def upsert(cfg: Settings, http: requests.Session, us: UserStory, key: str | None) -> tuple[str, str]:
    """Cria ou atualiza a story. Devolve (key, ação)."""
    for include_priority in (True, False):
        if key:
            res = http.put(
                f"{cfg.atlassian_root}/rest/api/3/issue/{key}",
                json={"fields": build_fields(us, cfg.jira_project_key, include_priority=include_priority, for_create=False)},
                auth=cfg.atlassian_auth,
                timeout=HTTP_TIMEOUT_S,
            )
        else:
            res = http.post(
                f"{cfg.atlassian_root}/rest/api/3/issue",
                json={"fields": build_fields(us, cfg.jira_project_key, include_priority=include_priority, for_create=True)},
                auth=cfg.atlassian_auth,
                timeout=HTTP_TIMEOUT_S,
            )
        if include_priority and _priority_rejected(res):
            print("  ⚠️  Campo Priority não disponível neste projeto — a repetir sem prioridade.")
            continue
        _raise_for(res, "atualização" if key else "criação")
        return (key, "atualizada") if key else (res.json()["key"], "criada")
    raise JiraError("estado inesperado no upsert")  # inalcançável


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Publica uma User Story no Jira Cloud.")
    p.add_argument("--story", type=int, required=True, help="número da story (1..N) em requirements/user_stories.json")
    p.add_argument("--key", help="key de uma issue existente a atualizar (ex.: QAAGENT-1)")
    p.add_argument("--dry-run", action="store_true", help="mostra o payload sem chamar a API")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        stories = load_stories()
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"❌ Ficheiro de stories inválido ({STORIES_FILE.name}): {exc}")
        return 1

    if not 1 <= args.story <= len(stories):
        print(f"❌ --story tem de estar entre 1 e {len(stories)}")
        return 1
    us = stories[args.story - 1]

    if args.dry_run:
        payload = build_fields(us, "<PROJECT_KEY>", include_priority=True, for_create=args.key is None)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    try:
        cfg = load_settings()
    except ValidationError as exc:
        print(f"❌ .env inválido: {exc}")
        return 1

    http = build_session()
    print(f"→ {us.id.upper()} · {us.summary}")
    try:
        key = args.key or find_by_label(cfg, http, us.id)
        key, action = upsert(cfg, http, us, key)
    except (JiraError, requests.RequestException) as exc:
        print(f"❌ {exc}")
        return 1

    print(f"✅ {key} {action} — {cfg.atlassian_root}/browse/{key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
