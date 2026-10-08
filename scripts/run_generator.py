"""Executa o Agente Gerador a partir da especificação produzida pelo Analista.

Uso:
    python scripts/run_generator.py QAAGENT-6

Pré-requisito: outputs/<KEY>/analysis.json (python scripts/run_analyst.py <KEY>).
Resultado em outputs/<KEY>/:
    <key>.feature       Gherkin em português (determinístico, a partir do Analista)
    test_<key>.py       testes pytest + Playwright gerados pelo LLM
    generation.json     contexto usado, pesquisa por passo, pressupostos e métricas
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.sanity_check import load_settings  # noqa: E402
from src.agents.generator import assemble_module, generate  # noqa: E402
from src.agents.gherkin import render_feature  # noqa: E402
from src.agents.models import AnalysisSpec  # noqa: E402
from src.llm.structured import LLMOutputError, temperature_supported  # noqa: E402
from src.rag.vector_store import KnowledgeStore  # noqa: E402

CHROMA_PATH = ROOT / "chroma_db"
OUTPUTS = ROOT / "outputs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agente Gerador: cenários → Gherkin + testes Playwright.")
    parser.add_argument("key", help="chave da User Story no Jira (ex.: QAAGENT-6)")
    args = parser.parse_args(argv)

    try:
        cfg = load_settings()
    except ValidationError as exc:
        print(f"❌ .env inválido: {exc}")
        return 1

    out_dir = OUTPUTS / args.key
    analysis_file = out_dir / "analysis.json"
    print(f"→ 1/4 A ler a especificação do Analista ({analysis_file.relative_to(ROOT)})")
    if not analysis_file.exists():
        print(f"❌ ficheiro inexistente: correr primeiro python scripts/run_analyst.py {args.key}")
        return 1
    try:
        analysis = json.loads(analysis_file.read_text(encoding="utf-8"))
        spec = AnalysisSpec.model_validate(analysis["spec"])
    except (KeyError, ValueError, ValidationError) as exc:
        print(f"❌ analysis.json inválido: {exc}")
        return 1
    title = analysis.get("story_summary", spec.story_key)
    print(f"  ✅ {len(spec.scenarios)} cenários · contexto do Analista {analysis.get('context_sections', [])}")

    stem = args.key.lower().replace("-", "_")
    feature_file = out_dir / f"{stem}.feature"
    feature_file.write_text(render_feature(spec, title), encoding="utf-8")
    print(f"→ 2/4 Gherkin gerado (sem LLM) → {feature_file.relative_to(ROOT)}")

    print(f"→ 3/4 A gerar os testes com {cfg.llm_model} (pesquisa RAG por passo)")
    try:
        result = generate(
            spec,
            KnowledgeStore(CHROMA_PATH),
            model=cfg.llm_model,
            api_key=cfg.anthropic_api_key.get_secret_value(),
            analyst_sections=analysis.get("context_sections", []),
        )
    except (LLMOutputError, ValueError, RuntimeError, KeyError) as exc:
        print(f"❌ {exc}")
        return 1

    suite, ctx, m = result.suite, result.context, result.metrics
    print(f"  ✅ {len(suite.tests)} funções de teste · secções usadas {ctx.sections}")
    print(f"     tentativas {m.attempts} · tokens {m.prompt_tokens}/{m.completion_tokens} · "
          f"{m.latency_ms / 1000:.1f} s · custo {'n/d' if m.cost_usd is None else f'${m.cost_usd:.4f}'}")
    if not temperature_supported(cfg.llm_model):
        print("     nota: o modelo não aceita temperature=0; usada a amostragem por omissão")
    if m.errors:
        print(f"     correções pedidas ao modelo: {len(m.errors)} · fim de cada tentativa {m.finish_reasons}")
    print("\n  Pesquisa por passo (passo → secções):")
    for step, sections in ctx.step_retrieval.items():
        print(f"     {sections}  {step}")

    test_file = out_dir / f"test_{stem}.py"
    test_file.write_text(assemble_module(suite, title), encoding="utf-8")
    print(f"\n→ 4/4 Testes → {test_file.relative_to(ROOT)}")
    for t in sorted(suite.tests, key=lambda t: t.scenario_id):
        print(f"     [{t.scenario_id}] {t.function_name}")
    if suite.assumptions:
        print("\n  ℹ️  Valores de exemplo assumidos pelo Gerador:")
        for a in suite.assumptions:
            print(f"     - {a}")

    (out_dir / "generation.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "model": cfg.llm_model,
                "temperature": 0 if temperature_supported(cfg.llm_model) else "omissão do modelo",
                "context_sections": ctx.sections,
                "step_retrieval": ctx.step_retrieval,
                "metrics": {
                    "attempts": m.attempts,
                    "prompt_tokens": m.prompt_tokens,
                    "completion_tokens": m.completion_tokens,
                    "latency_ms": m.latency_ms,
                    "cost_usd": m.cost_usd,
                    "finish_reasons": m.finish_reasons,
                    "correction_requests": m.errors,
                },
                "suite": suite.model_dump(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n  Executar: pytest {test_file.relative_to(ROOT)} -v")
    return 0


if __name__ == "__main__":
    sys.exit(main())
