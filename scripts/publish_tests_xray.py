"""Regista no Xray os testes gerados para uma User Story e liga-os à User Story no Jira.

Uso:
    python scripts/publish_tests_xray.py QAAGENT-6

Pré-requisitos (produzidos por python -m src.pipeline QAAGENT-6):
    outputs/<KEY>/analysis.json, generation.json e validation.json (aprovado).

Para cada cenário cria (ou atualiza, se já existir) um teste Xray do tipo Cucumber com os
passos Gherkin e liga-o à User Story ("tests / is tested by"). A operação é idempotente:
cada teste é identificado pela etiqueta <story>-<cenário> (ex.: qaagent-6-c01).
Resultado: outputs/<KEY>/xray.json (cenário → chave do teste Xray → função pytest).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.sanity_check import build_session, load_settings  # noqa: E402
from src.agents.gherkin import scenario_steps  # noqa: E402
from src.agents.models import AnalysisSpec  # noqa: E402
from src.integrations.xray_client import JiraLinks, XrayClient, XrayError  # noqa: E402

OUTPUTS = ROOT / "outputs"
GENERATED_LABEL = "gerado-ia"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regista os testes gerados no Xray e liga-os à User Story.")
    parser.add_argument("key", help="chave da User Story no Jira (ex.: QAAGENT-6)")
    args = parser.parse_args(argv)
    key = args.key
    out_dir = OUTPUTS / key

    try:
        cfg = load_settings()
    except ValidationError as exc:
        print(f"❌ .env inválido: {exc}")
        return 1

    try:
        analysis = json.loads((out_dir / "analysis.json").read_text(encoding="utf-8"))
        generation = json.loads((out_dir / "generation.json").read_text(encoding="utf-8"))
        validation = json.loads((out_dir / "validation.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        print(f"❌ ficheiro em falta ({exc.filename}): correr primeiro python -m src.pipeline {key}")
        return 1
    if not validation.get("approved"):
        print("❌ os testes não foram aprovados pelo Validador: não são registados no Xray")
        return 1

    spec = AnalysisSpec.model_validate(analysis["spec"])
    functions = {t["scenario_id"]: t["function_name"] for t in generation["suite"]["tests"]}
    http = build_session()
    xray = XrayClient(http, cfg.xray_root, cfg.xray_client_id.get_secret_value(),
                      cfg.xray_client_secret.get_secret_value())
    jira = JiraLinks(http, cfg.atlassian_root, cfg.atlassian_auth)
    story_label = key.lower()

    try:
        print("→ 1/3 A autenticar no Xray e a obter o tipo de ligação de testes do Jira")
        _ = xray.token
        link_type = jira.test_link_type()
        print(f"  ✅ token OAuth2 obtido · tipo de ligação \"{link_type}\"")

        print(f"→ 2/3 A registar {len(spec.scenarios)} testes Cucumber no Xray e a ligá-los a {key}")
        mapping: dict[str, dict[str, str]] = {}
        for sc in spec.scenarios:
            label = f"{story_label}-{sc.id.lower()}"
            summary = f"[{key}] {sc.id} – {sc.title}"
            gherkin = "\n".join(scenario_steps(sc))
            existing = jira.find_by_label(cfg.jira_project_key, label)
            if existing is None:
                ref = xray.create_cucumber_test(cfg.jira_project_key, summary, [GENERATED_LABEL, story_label, label], gherkin)
                action = "criado"
            else:
                ref = existing
                xray.update_gherkin(ref.issue_id, gherkin)
                jira.update_summary(ref.key, summary)
                action = "atualizado"
            link = jira.link_test_to_story(ref.key, key, link_type)
            mapping[sc.id] = {"test_key": ref.key, "issue_id": ref.issue_id, "function": functions.get(sc.id, "")}
            print(f"  ✅ {sc.id} → {ref.key} ({action}; ligação {link})  {sc.title}")

        print("→ 3/3 A verificar testes antigos desta User Story")
        current = {m["test_key"] for m in mapping.values()}
        obsolete = [k for k in jira.keys_by_labels(cfg.jira_project_key, [GENERATED_LABEL, story_label]) if k not in current]
        if obsolete:
            print(f"  ⚠️  testes de execuções anteriores sem cenário correspondente: {', '.join(obsolete)}"
                  " (rever ou remover no Jira)")
        else:
            print("  ✅ nenhum teste obsoleto")
    except (XrayError, requests.RequestException) as exc:
        print(f"❌ {exc}")
        return 1

    out = out_dir / "xray.json"
    out.write_text(json.dumps({
        "published_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "story": key,
        "tests": mapping,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  → mapeamento guardado em {out.relative_to(ROOT)}")
    print(f"  Confirmar no Jira: {cfg.atlassian_root}/browse/{key} (painel de cobertura do Xray)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
