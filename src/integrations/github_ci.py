"""Ligação do orquestrador à pipeline do GitHub Actions (requisito RF07).

1. push_outputs: publica os ficheiros gerados (outputs/<KEY>/) num ramo próprio
   (testes/<key>), criado a partir do main remoto, SEM alterar o ramo nem os ficheiros
   locais do utilizador (usa um índice Git temporário e comandos de baixo nível).
2. dispatch: dispara a pipeline com um evento repository_dispatch, indicando a User Story
   e o ramo onde estão os testes.

Configuração (.env): GITHUB_REPOSITORY (dono/repositório) e GITHUB_DISPATCH_TOKEN
(token com permissão "Contents: Read and write" apenas neste repositório).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import requests

HTTP_TIMEOUT_S = 30
EVENT_TYPE = "run-generated-tests"


class CIError(Exception):
    """Falha ao publicar os testes ou ao disparar a pipeline."""


def _git(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise CIError(f"git {' '.join(args[:2])}: {proc.stderr.strip()[:300]}")
    return proc.stdout.strip()


def branch_for(key: str) -> str:
    return f"testes/{key.lower()}"


def push_outputs(root: Path, key: str, *, remote: str = "origin", base: str = "main") -> tuple[str, str]:
    """Cria um commit com outputs/<KEY>/ sobre <remote>/<base> e envia-o para testes/<key>.

    Devolve (ramo, commit). Respeita o .gitignore (ficheiros de demonstração não seguem).
    """
    folder = root / "outputs" / key
    if not folder.is_dir():
        raise CIError(f"pasta inexistente: outputs/{key}")
    branch = branch_for(key)
    git_dir = Path(_git(["rev-parse", "--absolute-git-dir"], root))
    index = git_dir / "qaagent_publish_index"
    env = {**os.environ, "GIT_INDEX_FILE": str(index)}
    try:
        _git(["fetch", "-q", remote, base], root)
        _git(["read-tree", f"{remote}/{base}"], root, env)
        _git(["add", "--", f"outputs/{key}"], root, env)
        tree = _git(["write-tree"], root, env)
        commit = _git(["commit-tree", tree, "-p", f"{remote}/{base}",
                       "-m", f"chore(outputs): testes gerados para {key} [orquestrador]"], root, env)
        _git(["push", "-q", "--force", remote, f"{commit}:refs/heads/{branch}"], root)
    finally:
        index.unlink(missing_ok=True)
    return branch, commit


def dispatch(http: requests.Session, repository: str, token: str, key: str, ref: str) -> None:
    """Dispara a pipeline (evento repository_dispatch) para a User Story `key` no ramo `ref`."""
    r = http.post(
        f"https://api.github.com/repos/{repository}/dispatches",
        json={"event_type": EVENT_TYPE, "client_payload": {"story": key, "ref": ref}},
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=HTTP_TIMEOUT_S,
    )
    if r.status_code != 204:
        hint = {401: "token inválido", 403: "token sem permissão Contents: write", 404: "repositório inexistente ou sem acesso"}
        raise CIError(f"GitHub dispatch: HTTP {r.status_code} ({hint.get(r.status_code, 'erro')}) — {r.text[:200]}")
