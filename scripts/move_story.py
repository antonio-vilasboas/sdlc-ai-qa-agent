"""Move uma User Story para uma coluna do quadro do Jira (usado pela pipeline do GitHub Actions).

Uso:
    python scripts/move_story.py QAAGENT-6 "Automated Execution"

Credenciais: ATLASSIAN_BASE_URL, ATLASSIAN_USER_EMAIL e ATLASSIAN_API_TOKEN (ambiente ou .env).
Nunca falha a pipeline: se não for possível mover, mostra um aviso e termina com código 0.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.sanity_check import build_session  # noqa: E402
from src.integrations.jira_board import credentials_from_env, try_move  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print('uso: python scripts/move_story.py <CHAVE> "<coluna>"')
        return 2
    load_dotenv(ROOT / ".env")
    creds = credentials_from_env()
    if creds is None:
        print("  ⚠️  quadro: credenciais do Jira não definidas; User Story não movida")
        return 0
    try_move(build_session(), creds[0], creds[1], args[0], args[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
