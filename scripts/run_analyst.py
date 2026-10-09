"""Executa o Agente Analista para uma User Story e guarda a especificação produzida.

Uso:
    python scripts/run_analyst.py QAAGENT-2

Resultado: outputs/<KEY>/analysis.json (especificação + contexto usado + métricas).
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
from src.agents.analyst import analyse  # noqa: E402
from src.integrations.jira_reader import JiraReadError, fetch_story  # noqa: E402
from src.llm.structured import LLMOutputError, temperature_supported  # noqa: E402
from src.rag.vector_store import KnowledgeStore  # noqa: E402

CHROMA_PATH = ROOT / "chroma_db"
OUTPUTS = ROOT / "outputs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agente Analista: User Story → cenários de teste.")
    parser.add_argument("key", help="chave da User Story no Jira (ex.: QAAGENT-2)")
    args = parser.parse_args(argv)

    try:
        cfg = load_settings()
    except ValidationError as exc:
        print(f"❌ .env inválido: {exc}")
        return 1

    print(f"→ 1/3 A ler {args.key} do Jira")
    try:
        story = fetch_story(build_session(), cfg.atlassian_root, cfg.atlassian_auth, args.key)
    except (JiraReadError, requests.RequestException) as exc:
        print(f"❌ {exc}")
        return 1
    print(f"  ✅ {story.summary}")

    print(f"→ 2/3 A analisar com {cfg.llm_model} (contexto: secção 0 + 5 secções do RAG)")
    try:
        result = analyse(
            story,
            KnowledgeStore(CHROMA_PATH),
            model=cfg.llm_model,
            api_key=cfg.anthropic_api_key.get_secret_value(),
        )
    except (LLMOutputError, ValueError, RuntimeError) as exc:
        print(f"❌ {exc}")
        return 1

    spec, m = result.spec, result.metrics
    print(f"  ✅ {len(spec.scenarios)} cenários · secções usadas {result.context_sections}")
    print(f"     tentativas {m.attempts} · tokens {m.prompt_tokens}/{m.completion_tokens} · "
          f"{m.latency_ms / 1000:.1f} s · custo {'n/d' if m.cost_usd is None else f'${m.cost_usd:.4f}'}")
    if not temperature_supported(cfg.llm_model):
        print("     nota: o modelo não aceita temperature=0; usada a amostragem por omissão")
    if m.errors:
        print(f"     correções pedidas ao modelo: {len(m.errors)}")

    print("→ 3/3 Especificação")
    print(f"  Objetivo: {spec.summary}")
    for sc in spec.scenarios:
        print(f"\n  [{sc.id}] {sc.title}  ({sc.type})  regras {', '.join(sc.rules)} · critérios {sc.criteria}")
        for label, steps in (("Dado", sc.given), ("Quando", sc.when), ("Então", sc.then)):
            for i, step in enumerate(steps):
                print(f"     {label if i == 0 else 'E':<6} {step}")
        if sc.test_data:
            print(f"     dados: {sc.test_data}")
    if spec.gaps:
        print("\n  ⚠️  Lacunas identificadas:")
        for g in spec.gaps:
            print(f"     - {g}")

    out = OUTPUTS / args.key / "analysis.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "story_summary": story.summary,
                "model": cfg.llm_model,
                "temperature": 0 if temperature_supported(cfg.llm_model) else "omissão do modelo",
                "context_sections": result.context_sections,
                "metrics": {
                    "attempts": m.attempts,
                    "prompt_tokens": m.prompt_tokens,
                    "completion_tokens": m.completion_tokens,
                    "latency_ms": m.latency_ms,
                    "cost_usd": m.cost_usd,
                    "finish_reasons": m.finish_reasons,
                    "correction_requests": m.errors,
                },
                "spec": spec.model_dump(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n  → guardado em {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
