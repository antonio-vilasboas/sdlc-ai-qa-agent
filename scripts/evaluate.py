"""Avaliação experimental do protótipo (métricas AR, PER e ET do subcapítulo 5.5.2).

Fase 1 — execução (≈15 min, ≈ US$ 0,10 com 6 User Stories × 3 execuções):
    python scripts/evaluate.py --runs 3

    Para cada User Story e cada execução: corre o fluxo completo dos agentes (sem mexer no
    quadro do Jira nem no Xray), executa os testes gerados com o pytest e guarda tudo em
    outputs/_avaliacao/run<N>/<KEY>/. Gera ainda outputs/_avaliacao/revisao_ar.csv para a
    revisão humana dos cenários da 1.ª execução.

Fase 2 — revisão humana: abrir revisao_ar.csv e preencher a coluna "valido" (S/N) de cada
    cenário (o cenário verifica corretamente o critério de aceitação e as regras indicadas?).

Fase 3 — resumo:
    python scripts/evaluate.py --summarize --t-manual QAAGENT-2=40

    Calcula, por User Story e no total:
      PER  = testes executados com sucesso / testes gerados (média das execuções)
      AR   = cenários marcados como válidos / cenários revistos (1.ª execução)
      Cobertura de regras (indicador automático) = regras da secção 10 citadas nos cenários
      ET   = (T_manual − T_auto) / T_manual, para as User Stories com tempo manual medido
    Resultado: outputs/_avaliacao/resultados.md e resultados.json.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.report_xray import junit_results  # noqa: E402

EVAL_DIR = ROOT / "outputs" / "_avaliacao"
KB_FILE = ROOT / "knowledge" / "swaglabs_knowledge_base.md"
STORIES = [f"QAAGENT-{n}" for n in range(1, 7)]
_RANGE = re.compile(r"(RN-[A-Z]+-)(\d{2}) a RN-[A-Z]+-(\d{2})")
_RULE = re.compile(r"RN-[A-Z]+-\d{2}")


# -- gabarito (secção 10 da base de conhecimento) ------------------------------------
def expected_rules(kb_text: str) -> dict[str, set[str]]:
    """{User Story: regras esperadas}, expandindo intervalos como "RN-CHK-01 a RN-CHK-06"."""
    section = kb_text.split("## 10.", 1)[1]
    result: dict[str, set[str]] = {}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not re.fullmatch(r"QAAGENT-\d+", cells[0]):
            continue
        text = cells[2]
        rules = set(_RULE.findall(_RANGE.sub("", text)))
        for prefix, start, end in _RANGE.findall(text):
            rules.update(f"{prefix}{i:02d}" for i in range(int(start), int(end) + 1))
        result[cells[0]] = rules
    return result


# -- fase 1: execução ----------------------------------------------------------------
def run_pytest(test_file: Path, junit: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-q", f"--junitxml={junit}"],
        cwd=ROOT, capture_output=True, text=True, timeout=600, check=False,
    )
    if not junit.exists():
        return {"total": 0, "passed": 0, "error": proc.stdout[-500:] + proc.stderr[-500:]}
    results = junit_results(junit)
    passed = sum(r["status"] == "PASSED" for r in results.values())
    failed = {name: r["message"][:300] for name, r in results.items() if r["status"] != "PASSED"}
    return {"total": len(results), "passed": passed, "failed": failed}


def execute(stories: list[str], runs: int) -> int:
    from src.pipeline import run as run_pipeline  # import tardio (carrega LLM e ChromaDB)

    for n in range(1, runs + 1):
        root = EVAL_DIR / f"run{n}"
        for key in stories:
            print(f"\n{'=' * 70}\n[avaliação] execução {n}/{runs} · {key}\n{'=' * 70}")
            out_dir = root / key
            code = run_pipeline(key, out_root=root, board=False)
            record: dict[str, Any] = {"story": key, "run": n, "pipeline_exit": code}
            test_file = out_dir / f"test_{key.lower().replace('-', '_')}.py"
            if test_file.exists():
                record["pytest"] = run_pytest(test_file, out_dir / "junit.xml")
                p = record["pytest"]
                print(f"[avaliação] pytest: {p['passed']}/{p['total']} testes com sucesso")
            (out_dir / "avaliacao.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    write_review_sheet(stories)
    print(f"\n✅ Execuções concluídas. Próximo passo: preencher {EVAL_DIR.relative_to(ROOT)}/revisao_ar.csv"
          " (coluna valido = S/N) e correr --summarize.")
    return 0


def write_review_sheet(stories: list[str]) -> None:
    """Folha de revisão humana dos cenários da 1.ª execução (não substitui uma folha já preenchida)."""
    sheet = EVAL_DIR / "revisao_ar.csv"
    if sheet.exists():
        print(f"ℹ️  {sheet.relative_to(ROOT)} já existe: não foi substituída")
        return
    gabarito = expected_rules(KB_FILE.read_text(encoding="utf-8"))
    with sheet.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["story", "cenario", "tipo", "titulo", "criterios", "regras_citadas",
                    "regras_esperadas_us", "passos", "valido", "observacao"])
        for key in stories:
            analysis = EVAL_DIR / "run1" / key / "analysis.json"
            if not analysis.exists():
                continue
            spec = json.loads(analysis.read_text(encoding="utf-8"))["spec"]
            for sc in spec["scenarios"]:
                steps = " | ".join([*(f"Dado {s}" for s in sc["given"]), *(f"Quando {s}" for s in sc["when"]),
                                    *(f"Então {s}" for s in sc["then"])])
                w.writerow([key, sc["id"], sc["type"], sc["title"], ",".join(map(str, sc["criteria"])),
                            ",".join(sc["rules"]), ",".join(sorted(gabarito.get(key, set()))), steps, "", ""])


# -- fase 3: resumo -------------------------------------------------------------------
def _pct(a: float, b: float) -> float | None:
    return round(100 * a / b, 1) if b else None


def summarize(stories: list[str], t_manual: dict[str, float]) -> int:
    gabarito = expected_rules(KB_FILE.read_text(encoding="utf-8"))
    review: dict[str, list[str]] = {}
    sheet = EVAL_DIR / "revisao_ar.csv"
    if sheet.exists():
        with sheet.open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f, delimiter=";"):
                review.setdefault(row["story"], []).append(row["valido"].strip().upper()[:1])

    rows: list[dict[str, Any]] = []
    for key in stories:
        runs = sorted(EVAL_DIR.glob(f"run*/{key}/pipeline.json"))
        per_runs, cov_runs, times, costs, scen, rounds = [], [], [], [], [], []
        for pj in runs:
            d = pj.parent
            pipe = json.loads(pj.read_text(encoding="utf-8"))
            ev = json.loads((d / "avaliacao.json").read_text(encoding="utf-8")) if (d / "avaliacao.json").exists() else {}
            spec = json.loads((d / "analysis.json").read_text(encoding="utf-8"))["spec"]
            cited = {r for sc in spec["scenarios"] for r in sc["rules"]}
            exp = gabarito.get(key, set())
            py = ev.get("pytest", {})
            per_runs.append(_pct(py.get("passed", 0), py.get("total", 0)) or 0.0)
            cov_runs.append(_pct(len(cited & exp), len(exp)) or 0.0)
            times.append(pipe["wall_time_s"])
            costs.append(pipe.get("total_cost_usd") or 0.0)
            scen.append(pipe["scenarios"])
            rounds.append(pipe["rounds"])
        if not runs:
            continue
        marks = [m for m in review.get(key, []) if m in ("S", "N")]
        t_auto = statistics.mean(times)
        row = {
            "story": key,
            "execucoes": len(runs),
            "cenarios_medio": round(statistics.mean(scen), 1),
            "cenarios_min_max": f"{min(scen)}–{max(scen)}",
            "rondas_validador_max": max(rounds),
            "per_medio": round(statistics.mean(per_runs), 1),
            "per_por_execucao": per_runs,
            "cobertura_regras_medio": round(statistics.mean(cov_runs), 1),
            "ar": _pct(marks.count("S"), len(marks)),
            "cenarios_revistos": len(marks),
            "t_auto_s": round(t_auto, 1),
            "custo_medio_usd": round(statistics.mean(costs), 4),
        }
        if key in t_manual:
            tm = t_manual[key] * 60
            row["t_manual_s"] = tm
            row["et"] = round(100 * (tm - t_auto) / tm, 1)
        rows.append(row)

    def overall(field: str) -> float | None:
        vals = [r[field] for r in rows if r.get(field) is not None]
        return round(statistics.mean(vals), 1) if vals else None

    all_marks = [m for k in stories for m in review.get(k, []) if m in ("S", "N")]
    total = {
        "per_medio": overall("per_medio"),
        "cobertura_regras_medio": overall("cobertura_regras_medio"),
        "ar": _pct(all_marks.count("S"), len(all_marks)),
        "et": overall("et"),
        "t_auto_medio_s": overall("t_auto_s"),
        "custo_total_usd": round(sum(r["custo_medio_usd"] * r["execucoes"] for r in rows), 4),
    }
    (EVAL_DIR / "resultados.json").write_text(json.dumps({"por_story": rows, "global": total},
                                                         ensure_ascii=False, indent=2), encoding="utf-8")

    def fmt(v: Any, suffix: str = "") -> str:
        return "—" if v is None else f"{v}{suffix}".replace(".", ",")

    lines = [
        "| User Story | Cenários (mín.–máx.) | PER | Cobertura de regras | AR | T_auto | ET | Custo médio |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['story']} | {r['cenarios_min_max']} | {fmt(r['per_medio'], ' %')} | "
                     f"{fmt(r['cobertura_regras_medio'], ' %')} | {fmt(r['ar'], ' %')} | {fmt(r['t_auto_s'], ' s')} | "
                     f"{fmt(r.get('et'), ' %')} | US$ {fmt(r['custo_medio_usd'])} |")
    lines.append(f"| **Global** | | **{fmt(total['per_medio'], ' %')}** | **{fmt(total['cobertura_regras_medio'], ' %')}** | "
                 f"**{fmt(total['ar'], ' %')}** | {fmt(total['t_auto_medio_s'], ' s')} | **{fmt(total['et'], ' %')}** | "
                 f"total US$ {fmt(total['custo_total_usd'])} |")
    md = "\n".join(lines)
    (EVAL_DIR / "resultados.md").write_text(md + "\n", encoding="utf-8")
    print(md)
    print(f"\n→ guardado em {EVAL_DIR.relative_to(ROOT)}/resultados.md e resultados.json")
    if len(all_marks) == 0:
        print("⚠️  AR por calcular: preencher a coluna 'valido' em revisao_ar.csv")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Avaliação: métricas AR, PER e ET.")
    parser.add_argument("stories", nargs="*", default=STORIES, help="User Stories (por omissão QAAGENT-1 a 6)")
    parser.add_argument("--runs", type=int, default=3, help="execuções por User Story (por omissão 3)")
    parser.add_argument("--summarize", action="store_true", help="apenas calcular o resumo das execuções existentes")
    parser.add_argument("--t-manual", action="append", default=[], metavar="KEY=MIN",
                        help="tempo manual medido em minutos (ex.: QAAGENT-2=40); pode repetir-se")
    args = parser.parse_args(argv)
    t_manual = {k: float(v) for k, v in (item.split("=", 1) for item in args.t_manual)}
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    if args.summarize:
        return summarize(args.stories, t_manual)
    code = execute(args.stories, args.runs)
    summarize(args.stories, t_manual)
    return code


if __name__ == "__main__":
    sys.exit(main())
