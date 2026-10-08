"""Ingestão da base de conhecimento do Confluence no ChromaDB e avaliação da recuperação.

Passos:
  1. lê a página "Swag Labs – Base de Conhecimento QA" do Confluence (API REST v2);
  2. divide-a em secções (uma por título H2) e indexa cada secção no ChromaDB local
     (pasta chroma_db/, excluída do Git), com embeddings multilingues;
  3. avalia a recuperação: para cada User Story (requirements/user_stories.json) pesquisa
     o índice e compara as secções devolvidas com as esperadas na secção de
     rastreabilidade da própria página (gabarito). Métricas: Recall@k e Hit@k.

O resultado da avaliação é guardado em knowledge/rag_retrieval_eval.json.

Uso:
    python scripts/ingest_kb.py
    python scripts/ingest_kb.py --query "utilizador bloqueado não consegue entrar"
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
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.sanity_check import build_session, load_settings  # noqa: E402
from src.rag.confluence_source import ConfluenceSourceError, fetch_page  # noqa: E402
from src.rag.kb_parser import parse_storage, traceability  # noqa: E402
from src.rag.vector_store import KnowledgeStore  # noqa: E402

PAGE_TITLE = "Swag Labs – Base de Conhecimento QA"
CHROMA_PATH = ROOT / "chroma_db"
STORIES_FILE = ROOT / "requirements" / "user_stories.json"
EVAL_OUT = ROOT / "knowledge" / "rag_retrieval_eval.json"
K_VALUES = (3, 5)


def story_query(story: dict[str, Any]) -> str:
    """Texto de pesquisa construído a partir da User Story (o que o Agente Analista terá)."""
    s = story["story"]
    parts = [story["summary"], f"Como {s['como']}, quero {s['quero']}, para {s['para']}.", story["context"]]
    return "\n".join(parts + story["acceptance_criteria"])


def evaluate(store: KnowledgeStore, expected: dict[str, set[int]]) -> dict[str, Any]:
    stories: list[dict[str, Any]] = json.loads(STORIES_FILE.read_text(encoding="utf-8"))
    k_max = max(K_VALUES)
    per_story: list[dict[str, Any]] = []

    for story in stories:
        # us-0N corresponde a QAAGENT-N (as stories foram publicadas por esta ordem, ver 6.4.2)
        key = f"QAAGENT-{int(story['id'].split('-')[1])}"
        gold = expected.get(key)
        if gold is None:
            raise ValueError(f"{key} sem secções esperadas na rastreabilidade")
        t0 = time.perf_counter()
        hits = store.query(story_query(story), k=k_max)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        retrieved = [h.section_number for h in hits]
        row: dict[str, Any] = {
            "story": key,
            "expected_sections": sorted(gold),
            "retrieved": [{"section": h.section_number, "score": h.score} for h in hits],
            "query_latency_ms": latency_ms,
        }
        for k in K_VALUES:
            top = set(retrieved[:k])
            row[f"recall@{k}"] = round(len(top & gold) / len(gold), 3)
            row[f"hit@{k}"] = bool(top & gold)
        per_story.append(row)

    summary = {
        f"mean_recall@{k}": round(sum(r[f"recall@{k}"] for r in per_story) / len(per_story), 3) for k in K_VALUES
    } | {f"hit_rate@{k}": round(sum(r[f"hit@{k}"] for r in per_story) / len(per_story), 3) for k in K_VALUES}
    return {"summary": summary, "per_story": per_story}


def print_report(result: dict[str, Any]) -> None:
    print("\nAvaliação da recuperação (gabarito: secção de rastreabilidade da página)")
    print(f"{'Story':<11} {'Esperadas':<18} {'Top-5 devolvidas (secção:score)':<52} R@3   R@5")
    for r in result["per_story"]:
        top = " ".join(f"{x['section']}:{x['score']:.2f}" for x in r["retrieved"])
        print(f"{r['story']:<11} {str(r['expected_sections']):<18} {top:<52} {r['recall@3']:.2f}  {r['recall@5']:.2f}")
    s = result["summary"]
    print(f"\nRecall@3 médio: {s['mean_recall@3']:.3f} · Recall@5 médio: {s['mean_recall@5']:.3f}")
    print(f"Hit@3: {s['hit_rate@3']:.0%} · Hit@5: {s['hit_rate@5']:.0%}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingestão da base de conhecimento no ChromaDB.")
    parser.add_argument("--query", help="só pesquisa o índice existente (não reindexa)")
    parser.add_argument("-k", type=int, default=3, help="n.º de secções a devolver com --query")
    args = parser.parse_args(argv)

    store = KnowledgeStore(CHROMA_PATH)

    if args.query:
        for h in store.query(args.query, k=args.k):
            print(f"[{h.score:.3f}] {h.section_title}")
        return 0

    try:
        cfg = load_settings()
    except ValidationError as exc:
        print(f"❌ .env inválido: {exc}")
        return 1

    print(f"→ 1/3 A ler '{PAGE_TITLE}' do Confluence")
    try:
        page = fetch_page(build_session(), cfg.atlassian_root, cfg.atlassian_auth, cfg.confluence_space_key, PAGE_TITLE)
        sections = parse_storage(page.storage_xhtml)
        expected = traceability(sections)
    except (ConfluenceSourceError, requests.RequestException, ValueError) as exc:
        print(f"❌ {exc}")
        return 1
    print(f"  ✅ página {page.page_id} (versão {page.version}) · {len(sections)} secções")

    print(f"→ 2/3 A indexar no ChromaDB ({store.model_name})")
    t0 = time.perf_counter()
    count = store.rebuild(sections, {"page_id": page.page_id, "page_version": page.version, "page_url": page.web_url})
    print(f"  ✅ {count} blocos indexados em {time.perf_counter() - t0:.1f} s → {CHROMA_PATH.name}/")

    print("→ 3/3 A avaliar a recuperação com as 6 User Stories")
    result = evaluate(store, expected)
    print_report(result)

    EVAL_OUT.write_text(
        json.dumps(
            {
                "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "embedding_model": store.model_name,
                "chunking": "uma secção (H2) por bloco",
                "page": {"id": page.page_id, "version": page.version},
                **result,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n  → resultados guardados em {EVAL_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
