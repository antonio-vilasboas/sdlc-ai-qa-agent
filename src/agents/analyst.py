"""Agente Analista de Requisitos.

Entrada: User Story do Jira + contexto recuperado da base de conhecimento (RAG).
Saída: AnalysisSpec — cenários de teste em linguagem de negócio, cada um ligado às
regras de negócio (RN) e aos critérios de aceitação que cobre.

O agente NÃO escreve código nem seletores: decide apenas o que deve ser testado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.agents.models import AnalysisSpec
from src.integrations.jira_reader import JiraStory
from src.llm.structured import CallMetrics, call_structured, schema_hint
from src.rag.vector_store import Hit, KnowledgeStore

RAG_K = 5  # n.º de secções recuperadas (subcapítulo 6.6.3)
ALWAYS_INCLUDED = (0,)  # secção de convenções, sempre presente

SYSTEM_PROMPT = """És o Agente Analista de Requisitos de uma equipa de QA (garantia de qualidade).
Recebes uma User Story do Jira e excertos da base de conhecimento da aplicação (Confluence).
A tua tarefa é especificar os cenários de teste E2E necessários para validar a User Story.

Regras obrigatórias:
1. Cada critério de aceitação da User Story tem de ser coberto por pelo menos um cenário.
2. Usa APENAS informação presente na User Story ou no contexto. Nunca inventes mensagens,
   dados, credenciais, regras ou comportamentos.
3. Em cada cenário indica as regras de negócio (IDs RN-...) do contexto que o cenário verifica.
   Usa apenas IDs que aparecem no contexto.
4. Escreve os passos em linguagem de negócio, em português. Não incluas seletores, código
   nem nomes de atributos técnicos (ex.: valores data-test, ids, classes CSS) — nem nos
   passos nem em test_data. A tradução para elementos da página é feita por outro agente.
5. Em test_data coloca apenas dados de negócio concretos, copiados do contexto (utilizador,
   password, textos exatos esperados, valores, URL de destino).
6. Em gaps regista apenas comportamentos da aplicação relevantes para os cenários que não
   estão especificados na User Story nem no contexto. Não comentes o processo de análise
   nem a origem da informação.

Responde APENAS com um objeto JSON válido, sem texto antes ou depois, conforme este esquema:
{schema}"""

USER_TEMPLATE = """## User Story
{story}

## Contexto da base de conhecimento
{context}"""

_CRITERION = re.compile(r"^(\d+)\.\s", re.M)


@dataclass(frozen=True)
class AnalystResult:
    spec: AnalysisSpec
    context_sections: list[int]
    metrics: CallMetrics


def build_context(store: KnowledgeStore, story: JiraStory, k: int = RAG_K) -> list[Hit]:
    """Secção 0 (sempre) + as k secções mais relevantes para a User Story."""
    always = [store.get_section(n) for n in ALWAYS_INCLUDED]
    return always + store.query(story.as_text(), k=k, exclude_sections=ALWAYS_INCLUDED)


def acceptance_criteria_count(story: JiraStory) -> int:
    """N.º de critérios de aceitação (lista numerada na secção respetiva da descrição)."""
    part = story.description.split("## Critérios de Aceitação", 1)
    if len(part) < 2:
        return 0
    section = part[1].split("\n## ", 1)[0]
    return len(_CRITERION.findall(section))


def _checker(context: list[Hit], n_criteria: int, story_key: str):  # type: ignore[no-untyped-def]
    known_rules = {r for h in context for r in str(h.metadata.get("rule_ids", "")).split(",") if r}

    def check(spec: AnalysisSpec) -> list[str]:
        problems: list[str] = []
        if spec.story_key != story_key:
            problems.append(f"story_key deve ser {story_key}")
        for sc in spec.scenarios:
            unknown = [r for r in sc.rules if r not in known_rules]
            if unknown:
                problems.append(f"{sc.id}: regras inexistentes no contexto {unknown}; usa apenas {sorted(known_rules)}")
            invalid = [c for c in sc.criteria if not 1 <= c <= n_criteria]
            if invalid:
                problems.append(f"{sc.id}: critérios inválidos {invalid} (a User Story tem {n_criteria})")
        covered = {c for sc in spec.scenarios for c in sc.criteria}
        missing = sorted(set(range(1, n_criteria + 1)) - covered)
        if missing:
            problems.append(f"critérios de aceitação sem cenário: {missing}")
        return problems

    return check


def analyse(story: JiraStory, store: KnowledgeStore, *, model: str, api_key: str) -> AnalystResult:
    context = build_context(store, story)
    n_criteria = acceptance_criteria_count(story)
    if n_criteria == 0:
        raise ValueError(f"{story.key}: critérios de aceitação não encontrados na descrição")

    result = call_structured(
        model=model,
        api_key=api_key,
        system=SYSTEM_PROMPT.format(schema=schema_hint(AnalysisSpec)),
        user=USER_TEMPLATE.format(story=story.as_text(), context="\n\n".join(h.content for h in context)),
        schema=AnalysisSpec,
        extra_check=_checker(context, n_criteria, story.key),
        max_tokens=8000,  # 4000 truncou a QAAGENT-6 (6 cenários) numa execução do orquestrador
    )
    return AnalystResult(
        spec=result.value,
        context_sections=[h.section_number for h in context],
        metrics=result.metrics,
    )
