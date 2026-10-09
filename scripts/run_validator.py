"""Executa o Agente Validador sobre os testes gerados para uma User Story.

Uso:
    python scripts/run_validator.py QAAGENT-6
    python scripts/run_validator.py QAAGENT-6 --file outro_ficheiro.py   (validar outro módulo)

Pré-requisitos: outputs/<KEY>/analysis.json e outputs/<KEY>/test_<key>.py.
Resultado: outputs/<KEY>/validation.json (ou validation_<ficheiro>.json com --file). Código de saída 0 = aprovado, 1 = rejeitado.
Não usa o LLM nem abre o browser (análise estática com o módulo ast).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.agents.validator import allowed_selectors, validate  # noqa: E402
from src.rag.vector_store import KnowledgeStore  # noqa: E402

CHROMA_PATH = ROOT / "chroma_db"
OUTPUTS = ROOT / "outputs"
RULES = {
    "V1": "sintaxe Python válida",
    "V2": "apenas importações permitidas",
    "V3": "sem esperas fixas nem chamadas proibidas",
    "V4": "seletores data-test existentes na base de conhecimento",
    "V5": "pelo menos uma asserção expect por teste",
    "V6": "uma função de teste por cenário",
    "V7": "cada teste começa com page.goto (aviso)",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agente Validador: análise estática dos testes gerados.")
    parser.add_argument("key", help="chave da User Story no Jira (ex.: QAAGENT-6)")
    parser.add_argument("--file", type=Path, help="módulo de testes a validar (por omissão: outputs/<KEY>/test_<key>.py)")
    args = parser.parse_args(argv)

    out_dir = OUTPUTS / args.key
    stem = args.key.lower().replace("-", "_")
    test_file = args.file or out_dir / f"test_{stem}.py"
    analysis_file = out_dir / "analysis.json"
    for f in (test_file, analysis_file):
        if not f.exists():
            print(f"❌ ficheiro inexistente: {f}")
            return 1

    print(f"→ 1/3 A carregar a lista de seletores da base de conhecimento ({CHROMA_PATH.name}/)")
    try:
        allowed = allowed_selectors(h.content for h in KnowledgeStore(CHROMA_PATH).all_sections())
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1
    if not allowed:
        print("❌ nenhum seletor encontrado: executar primeiro python scripts/ingest_kb.py")
        return 1
    print(f"  ✅ {len(allowed)} seletores data-test documentados")

    scenarios = [s["id"] for s in json.loads(analysis_file.read_text(encoding="utf-8"))["spec"]["scenarios"]]
    print(f"→ 2/3 A analisar {test_file.name} ({len(scenarios)} cenários esperados: {', '.join(scenarios)})")
    report = validate(test_file.read_text(encoding="utf-8"), allowed, scenarios)

    print("→ 3/3 Resultado por regra")
    for rule, desc in RULES.items():
        found = [i for i in report.issues if i.rule == rule]
        mark = "✅" if not found else ("⚠️ " if all(i.severity == "aviso" for i in found) else "❌")
        print(f"  {mark} {rule}  {desc}" + (f"  ({len(found)})" if found else ""))
    for issue in report.issues:
        print(f"     - {issue}")

    print(f"\n  Testes analisados: {len(report.tests)} · seletores distintos usados: {len(report.selectors_used)} · "
          f"asserções expect: {sum(report.expects_per_test.values())}")
    print(f"  {'✅ APROVADO' if report.approved else '❌ REJEITADO'}"
          f" ({len(report.errors)} erros, {len(report.warnings)} avisos)")

    out = out_dir / ("validation.json" if args.file is None else f"validation_{test_file.stem}.json")
    out.write_text(
        json.dumps(
            {
                "validated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "file": test_file.name,
                "allowed_selectors": len(allowed),
                **report.model_dump(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n  → guardado em {out.relative_to(ROOT)}")
    return 0 if report.approved else 1


if __name__ == "__main__":
    sys.exit(main())
