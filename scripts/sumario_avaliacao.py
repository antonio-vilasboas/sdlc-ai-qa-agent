"""Sumário por execução da avaliação (outputs/_avaliacao/runN/<KEY>/pipeline.json)."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

BASE = Path("outputs/_avaliacao")
KNOWN_KEYS = {"story", "started_at", "model", "stages"}


def _metrics(stage: dict[str, Any] | None) -> tuple[int, int, int, float]:
    if not stage:
        return 0, 0, 0, 0.0
    return (
        int(stage.get("prompt_tokens", 0)),
        int(stage.get("completion_tokens", 0)),
        int(stage.get("latency_ms", 0)),
        float(stage.get("cost_usd", 0.0)),
    )


def summarise(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    stages = data.get("stages", {})
    rounds: list[dict[str, Any]] = stages.get("rounds", [])

    t_in = t_out = lat_ms = 0
    cost = 0.0
    for stage in [stages.get("analyst")] + [r.get("generator") for r in rounds]:
        a, b, c, d = _metrics(stage)
        t_in, t_out, lat_ms, cost = t_in + a, t_out + b, lat_ms + c, cost + d

    approved = next(
        (r.get("round") for r in rounds if r.get("validator", {}).get("approved")), None
    )
    return {
        "run": path.parent.parent.name,
        "story": data.get("story", path.parent.name),
        "started_at_utc": data.get("started_at", ""),
        "model": data.get("model", ""),
        "rondas": len(rounds),
        "aprovado_na_ronda": approved if approved is not None else "nao_aprovado",
        "tokens_in": t_in,
        "tokens_out": t_out,
        "tempo_agentes_s": round(lat_ms / 1000, 1),
        "custo_usd": round(cost, 6),
        "chaves_extra": ";".join(sorted(set(data) - KNOWN_KEYS)),
    }


def main() -> None:
    paths = sorted(BASE.glob("run*/QAAGENT-*/pipeline.json"))
    if not paths:
        raise SystemExit(f"Nenhum pipeline.json encontrado em {BASE}")
    rows = [summarise(p) for p in paths]

    out = BASE / "sumario_runs.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    for r in rows:
        print(f"{r['run']:5} {r['story']:10} {r['started_at_utc']:26} "
              f"ronda={r['aprovado_na_ronda']!s:12} {r['tempo_agentes_s']:6}s "
              f"in={r['tokens_in']:6} out={r['tokens_out']:6} US${r['custo_usd']:.4f} {r['chaves_extra']}")

    print(f"\nRuns: {len(rows)}  |  Aprovação: {dict(Counter(str(r['aprovado_na_ronda']) for r in rows))}")
    print(f"Custo total: US${sum(r['custo_usd'] for r in rows):.4f}  |  "
          f"Tempo médio agentes: {sum(r['tempo_agentes_s'] for r in rows) / len(rows):.1f}s")
    print(f"Datas: {min(r['started_at_utc'] for r in rows)} -> {max(r['started_at_utc'] for r in rows)}")
    print(f"CSV: {out}")


if __name__ == "__main__":
    main()
