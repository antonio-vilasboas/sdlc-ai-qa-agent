"""Orquestrador: executa o fluxo completo para uma User Story.

    Jira → Agente Analista → Gherkin → Agente Gerador ⇄ Agente Validador → ficheiros finais

No quadro do Jira, a User Story passa para "AI Generating Tests" no início e para
"In Review" quando os testes são aprovados pelo Validador.

Se o Validador rejeitar o código, os erros são devolvidos ao Gerador, que gera uma nova
versão (até MAX_ROUNDS rondas). Cada etapa regista tempo, tokens e custo, para a métrica
de Ganho de Eficiência Temporal (ET).

Uso:
    python -m src.pipeline QAAGENT-6
    python -m src.pipeline QAAGENT-6 --reuse-analysis   (reaproveita outputs/<KEY>/analysis.json)
    python -m src.pipeline QAAGENT-6 --publish          (+ Xray + GitHub Actions: ciclo completo)

Resultado em outputs/<KEY>/: analysis.json, <key>.feature, test_<key>.py, generation.json,
validation.json e pipeline.json (resumo e métricas por etapa).
Código de saída: 0 = testes aprovados pelo Validador; 1 = erro ou testes rejeitados.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.sanity_check import build_session, load_settings  # noqa: E402
from src.agents.analyst import analyse  # noqa: E402
from src.agents.generator import assemble_module, generate  # noqa: E402
from src.agents.gherkin import render_feature  # noqa: E402
from src.agents.models import AnalysisSpec  # noqa: E402
from src.agents.validator import allowed_selectors, validate  # noqa: E402
from src.integrations.github_ci import CIError, dispatch, push_outputs  # noqa: E402
from src.integrations.jira_board import GENERATING, IN_REVIEW, try_move  # noqa: E402
from src.integrations.jira_reader import JiraReadError, fetch_story  # noqa: E402
from src.llm.structured import CallMetrics, LLMOutputError, temperature_supported  # noqa: E402
from src.rag.vector_store import KnowledgeStore  # noqa: E402

CHROMA_PATH = ROOT / "chroma_db"
OUTPUTS = ROOT / "outputs"
MAX_ROUNDS = 2  # gerações no máximo: a inicial + 1 correção pedida pelo Validador


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _metrics(m: CallMetrics) -> dict[str, Any]:
    return {
        "attempts": m.attempts,
        "prompt_tokens": m.prompt_tokens,
        "completion_tokens": m.completion_tokens,
        "latency_ms": m.latency_ms,
        "cost_usd": m.cost_usd,
        "finish_reasons": m.finish_reasons,
        "correction_requests": m.errors,
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _fmt(m: CallMetrics) -> str:
    cost = "n/d" if m.cost_usd is None else f"${m.cost_usd:.4f}"
    return f"tentativas {m.attempts} · tokens {m.prompt_tokens}/{m.completion_tokens} · {m.latency_ms / 1000:.1f} s · {cost}"


def run(key: str, *, reuse_analysis: bool = False, publish: bool = False,
        out_root: Path | None = None, board: bool = True) -> int:  # noqa: PLR0911, PLR0915
    t_start = time.perf_counter()
    n_steps = 7 if publish else 4
    try:
        cfg = load_settings()
    except ValidationError as exc:
        print(f"❌ .env inválido: {exc}")
        return 1
    api_key = cfg.anthropic_api_key.get_secret_value()
    out_dir = (out_root or OUTPUTS) / key
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = key.lower().replace("-", "_")
    store = KnowledgeStore(CHROMA_PATH)
    summary: dict[str, Any] = {"story": key, "started_at": _now(), "model": cfg.llm_model, "stages": {}}
    http = build_session()
    if board:
        try_move(http, cfg.atlassian_root, cfg.atlassian_auth, key, GENERATING)

    # 1. Agente Analista ---------------------------------------------------------------
    analysis_file = out_dir / "analysis.json"
    if reuse_analysis and analysis_file.exists():
        print(f"→ 1/{n_steps} Analista: a reaproveitar {analysis_file.relative_to(ROOT)}")
        data = json.loads(analysis_file.read_text(encoding="utf-8"))
        spec = AnalysisSpec.model_validate(data["spec"])
        title = data.get("story_summary", key)
        analyst_sections = data.get("context_sections", [])
        summary["stages"]["analyst"] = {"reused": True}
    else:
        print(f"→ 1/{n_steps} Analista: a ler {key} do Jira e a especificar os cenários")
        try:
            story = fetch_story(http, cfg.atlassian_root, cfg.atlassian_auth, key)
            result = analyse(story, store, model=cfg.llm_model, api_key=api_key)
        except (JiraReadError, requests.RequestException, LLMOutputError, ValueError, RuntimeError) as exc:
            print(f"❌ {exc}")
            return 1
        spec, title, analyst_sections = result.spec, story.summary, result.context_sections
        _write_json(analysis_file, {
            "generated_at": _now(),
            "story_summary": story.summary,
            "model": cfg.llm_model,
            "temperature": 0 if temperature_supported(cfg.llm_model) else "omissão do modelo",
            "context_sections": analyst_sections,
            "metrics": _metrics(result.metrics),
            "spec": spec.model_dump(),
        })
        summary["stages"]["analyst"] = {"context_sections": analyst_sections, **_metrics(result.metrics)}
        print(f"  ✅ {len(spec.scenarios)} cenários · secções {analyst_sections} · {_fmt(result.metrics)}")
        if spec.gaps:
            print(f"  ⚠️  {len(spec.gaps)} lacunas registadas (ver analysis.json)")

    # 2. Gherkin (determinístico) ------------------------------------------------------
    feature_file = out_dir / f"{stem}.feature"
    feature_file.write_text(render_feature(spec, title), encoding="utf-8")
    print(f"→ 2/{n_steps} Gherkin: {feature_file.relative_to(ROOT)} (sem LLM)")

    # 3 e 4. Gerador ⇄ Validador ------------------------------------------------------
    allowed = allowed_selectors(h.content for h in store.all_sections())
    scenario_ids = [sc.id for sc in spec.scenarios]
    feedback: list[str] = []
    rounds: list[dict[str, Any]] = []
    test_file = out_dir / f"test_{stem}.py"
    report = None

    for rnd in range(1, MAX_ROUNDS + 1):
        label = "geração inicial" if rnd == 1 else f"correção pedida pelo Validador ({len(feedback)} erros)"
        print(f"→ 3/{n_steps} Gerador, ronda {rnd}: {label}")
        try:
            gen = generate(spec, store, model=cfg.llm_model, api_key=api_key,
                           analyst_sections=analyst_sections, feedback=feedback)
        except (LLMOutputError, ValueError, RuntimeError, KeyError) as exc:
            print(f"❌ {exc}")
            return 1
        code = assemble_module(gen.suite, title)
        test_file.write_text(code, encoding="utf-8")
        print(f"  ✅ {len(gen.suite.tests)} testes · secções {gen.context.sections} · {_fmt(gen.metrics)}")

        print(f"→ 4/{n_steps} Validador, ronda {rnd}")
        report = validate(code, allowed, scenario_ids)
        print(f"  {'✅ APROVADO' if report.approved else '❌ REJEITADO'} "
              f"({len(report.errors)} erros, {len(report.warnings)} avisos)")
        for issue in report.issues:
            print(f"     - {issue}")

        rounds.append({
            "round": rnd,
            "feedback_received": feedback,
            "generator": {"context_sections": gen.context.sections, **_metrics(gen.metrics)},
            "validator": {"approved": report.approved, "errors": [str(i) for i in report.errors],
                          "warnings": [str(i) for i in report.warnings]},
        })
        _write_json(out_dir / "generation.json", {
            "generated_at": _now(),
            "model": cfg.llm_model,
            "round": rnd,
            "context_sections": gen.context.sections,
            "step_retrieval": gen.context.step_retrieval,
            "metrics": _metrics(gen.metrics),
            "suite": gen.suite.model_dump(),
        })
        if report.approved:
            break
        feedback = [str(i) for i in report.errors]

    assert report is not None
    _write_json(out_dir / "validation.json", {"validated_at": _now(), "file": test_file.name,
                                              "allowed_selectors": len(allowed), **report.model_dump()})

    # Resumo ----------------------------------------------------------------------------
    costs = [summary["stages"].get("analyst", {}).get("cost_usd")] + [r["generator"]["cost_usd"] for r in rounds]
    known = [c for c in costs if c is not None]
    wall = round(time.perf_counter() - t_start, 1)
    summary["stages"]["rounds"] = rounds
    summary.update({
        "finished_at": _now(),
        "approved": report.approved,
        "rounds": len(rounds),
        "scenarios": len(spec.scenarios),
        "wall_time_s": wall,
        "total_cost_usd": round(sum(known), 6) if known else None,
        "files": [p.name for p in (analysis_file, feature_file, test_file)],
    })
    _write_json(out_dir / "pipeline.json", summary)

    print(f"\n{'✅' if report.approved else '❌'} {key}: {len(spec.scenarios)} cenários · {len(rounds)} ronda(s) · "
          f"{wall} s no total · custo ${summary['total_cost_usd'] or 0:.4f}")
    print(f"  → resultados em {out_dir.relative_to(ROOT)}/ (resumo em pipeline.json)")
    if not report.approved:
        return 1
    if board:
        try_move(http, cfg.atlassian_root, cfg.atlassian_auth, key, IN_REVIEW)
    if not publish:
        print(f"  Executar: pytest {test_file.relative_to(ROOT)} -v")
        print("  (com --publish: registo no Xray + execução automática no GitHub Actions)")
        return 0
    return _publish_and_dispatch(key, http)


def _publish_and_dispatch(key: str, http: requests.Session) -> int:
    """Etapas 5–7: registo no Xray, publicação dos testes num ramo e disparo da pipeline (RF06, RF07)."""
    from scripts.publish_tests_xray import main as publish_tests  # import tardio: só com --publish

    print("\n→ 5/7 Registo dos testes no Xray")
    if publish_tests([key]) != 0:
        return 1

    env = dotenv_values(ROOT / ".env")
    repository, token = env.get("GITHUB_REPOSITORY"), env.get("GITHUB_DISPATCH_TOKEN")
    if not repository or not token:
        print("❌ GITHUB_REPOSITORY e GITHUB_DISPATCH_TOKEN em falta no .env: pipeline não disparada")
        return 1
    try:
        print("→ 6/7 A publicar os testes gerados no GitHub")
        branch, commit = push_outputs(ROOT, key)
        print(f"  ✅ outputs/{key}/ → ramo {branch} (commit {commit[:7]})")
        print("→ 7/7 A disparar a pipeline do GitHub Actions (repository_dispatch)")
        dispatch(http, repository, token, key, branch)
    except (CIError, requests.RequestException) as exc:
        print(f"❌ {exc}")
        return 1
    print(f"  ✅ pipeline disparada: https://github.com/{repository}/actions")
    print("  A User Story passa a Automated Execution e, no fim, a Done (ou volta a In Review se houver falhas).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fluxo completo: User Story → testes validados.")
    parser.add_argument("key", help="chave da User Story no Jira (ex.: QAAGENT-6)")
    parser.add_argument("--reuse-analysis", action="store_true",
                        help="reaproveitar outputs/<KEY>/analysis.json em vez de chamar o Analista")
    parser.add_argument("--publish", action="store_true",
                        help="registar no Xray, publicar os testes e disparar a pipeline do GitHub Actions")
    args = parser.parse_args(argv)
    return run(args.key, reuse_analysis=args.reuse_analysis, publish=args.publish)


if __name__ == "__main__":
    sys.exit(main())
