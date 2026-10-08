"""Agente Gerador de Testes.

Entrada: especificação do Analista (AnalysisSpec) + contexto da base de conhecimento.
Saída: GeneratedSuite — uma função pytest/Playwright por cenário.

Contexto (decomposição da pesquisa, subcapítulo 6.7):
  - o Analista pesquisou com a User Story inteira ("o quê testar");
  - o Gerador precisa de saber "como" executar cada passo, por isso pesquisa também
    passo a passo (Dado/Quando/Então) e junta as secções encontradas às do Analista.

O módulo Python final é montado aqui: o cabeçalho (imports, URL base) é fixo e o LLM
escreve apenas o corpo das funções. O Gherkin é produzido de forma determinística
(src/agents/gherkin.py) e não passa pelo LLM.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from src.agents.gherkin import scenario_steps
from src.agents.models import AnalysisSpec, GeneratedSuite
from src.llm.structured import CallMetrics, call_structured, schema_hint
from src.rag.vector_store import Hit, KnowledgeStore

STEP_K = 2  # secções recuperadas por passo
ALWAYS_INCLUDED = (0,)
BASE_URL = "https://www.saucedemo.com"

MODULE_HEADER = '''"""Testes E2E gerados automaticamente pelo Agente Gerador — {key}: {title}

Não editar à mão: regenerar com `python scripts/run_generator.py {key}`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "{base_url}"
'''

SYSTEM_PROMPT = """És o Agente Gerador de uma equipa de QA (garantia de qualidade).
Recebes cenários de teste já aprovados (em linguagem de negócio) e excertos da base de
conhecimento da aplicação Swag Labs. Implementas cada cenário como uma função de teste
pytest com Playwright (Python, API síncrona).

Regras obrigatórias:
1. Exatamente uma função por cenário, com a assinatura
   `def test_<id em minúsculas>_<descrição_curta>(page: Page) -> None:` (ex.: test_c01_login_valido).
2. Seletores: usa APENAS valores data-test que aparecem no contexto, sempre na forma
   page.locator('[data-test="<valor>"]'). Em padrões como add-to-cart-<produto>, substitui
   <produto> pelo sufixo indicado na tabela de produtos. Nunca uses XPath, classes CSS,
   ids, get_by_role nem get_by_text.
3. Navegação: page.goto(BASE_URL + "<caminho>") com caminhos do contexto. A constante
   BASE_URL já existe no módulo.
4. Verificações: apenas com expect(...) do Playwright (to_have_text, to_contain_text,
   to_have_url, to_be_visible, to_have_count, to_have_value). Cada "Então" tem pelo menos
   um expect. Elemento que "deixa de ser apresentado"/"não existe" → to_have_count(0).
   Nunca uses time.sleep, wait_for_timeout nem assert sobre texto lido manualmente.
5. Antes do código de cada passo escreve um comentário com o passo, exatamente como
   recebido (ex.: `# Dado O utilizador está autenticado com um utilizador válido`).
6. Dados: usa os valores de test_data e do contexto (credenciais, textos exatos, preços).
   Nunca inventes credenciais, mensagens nem seletores. Só para campos de texto livre
   sem valor no contexto (ex.: primeiro nome, apelido, código postal) podes usar valores
   de exemplo neutros, e regista cada um em assumptions.
7. Cada teste é independente: começa na página de login e autentica-se se precisar.
   Não escrevas imports, fixtures, funções auxiliares nem código fora da função.
8. Em code coloca o código Python completo da função (linha def incluída), com
   indentação de 4 espaços.

Responde APENAS com um objeto JSON válido, sem texto antes ou depois, conforme este esquema:
{schema}"""

USER_TEMPLATE = """## User Story {key}
Objetivo dos testes: {summary}

## Cenários a implementar
{scenarios}

## Contexto da base de conhecimento
{context}"""


@dataclass(frozen=True)
class GeneratorContext:
    hits: list[Hit]
    step_retrieval: dict[str, list[int]]  # passo → secções recuperadas (rastreabilidade)

    @property
    def sections(self) -> list[int]:
        return [h.section_number for h in self.hits]


@dataclass(frozen=True)
class GeneratorResult:
    suite: GeneratedSuite
    context: GeneratorContext
    metrics: CallMetrics


def build_context(
    store: KnowledgeStore, spec: AnalysisSpec, analyst_sections: Iterable[int] = (), k: int = STEP_K
) -> GeneratorContext:
    """Secção 0 + secções do Analista + top-k secções de cada passo distinto."""
    step_retrieval: dict[str, list[int]] = {}
    found: dict[int, Hit] = {}
    for sc in spec.scenarios:
        for step in (*sc.given, *sc.when, *sc.then):
            if step in step_retrieval:
                continue
            hits = store.query(step, k=k, exclude_sections=ALWAYS_INCLUDED)
            step_retrieval[step] = [h.section_number for h in hits]
            for h in hits:
                found.setdefault(h.section_number, h)

    wanted = set(ALWAYS_INCLUDED) | set(analyst_sections) | set(found)
    hits = [found[n] if n in found else store.get_section(n) for n in sorted(wanted)]
    return GeneratorContext(hits=hits, step_retrieval=step_retrieval)


def _scenarios_payload(spec: AnalysisSpec) -> str:
    """Cenários enviados ao modelo (só o necessário para implementar)."""
    data = [
        {"id": sc.id, "title": sc.title, "steps": scenario_steps(sc), "test_data": sc.test_data}
        for sc in spec.scenarios
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def _checker(spec: AnalysisSpec):  # type: ignore[no-untyped-def]
    """Verificações estruturais (a validação de seletores e boas práticas é do Validador)."""
    expected = [sc.id for sc in spec.scenarios]

    def check(suite: GeneratedSuite) -> list[str]:
        problems: list[str] = []
        if suite.story_key != spec.story_key:
            problems.append(f"story_key deve ser {spec.story_key}")
        ids = [t.scenario_id for t in suite.tests]
        if sorted(ids) != sorted(expected):
            problems.append(f"tem de existir exatamente uma função por cenário {expected}; recebido {ids}")
        names = [t.function_name for t in suite.tests]
        if len(set(names)) != len(names):
            problems.append("nomes de funções repetidos")
        for t in suite.tests:
            problems += _check_function(t.scenario_id, t.function_name, t.code)
        return problems

    return check


def _check_function(scenario_id: str, name: str, code: str) -> list[str]:
    if not name.startswith(f"test_{scenario_id.lower()}_"):
        return [f"{scenario_id}: o nome da função deve começar por test_{scenario_id.lower()}_"]
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"{scenario_id}: erro de sintaxe na linha {exc.lineno}: {exc.msg}"]
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        return [f"{scenario_id}: code deve conter apenas a definição de uma função (sem imports nem outro código)"]
    fn = tree.body[0]
    problems: list[str] = []
    if fn.name != name:
        problems.append(f"{scenario_id}: a função chama-se {fn.name}, mas function_name é {name}")
    if [a.arg for a in fn.args.args] != ["page"]:
        problems.append(f"{scenario_id}: a função deve receber apenas o parâmetro page")
    return problems


def assemble_module(suite: GeneratedSuite, title: str) -> str:
    """Módulo pytest final: cabeçalho fixo + funções pela ordem dos cenários."""
    header = MODULE_HEADER.format(key=suite.story_key, title=title, base_url=BASE_URL)
    functions = [t.code.strip("\n") for t in sorted(suite.tests, key=lambda t: t.scenario_id)]
    return header + "\n\n" + "\n\n\n".join(functions) + "\n"


def generate(
    spec: AnalysisSpec,
    store: KnowledgeStore,
    *,
    model: str,
    api_key: str,
    analyst_sections: Sequence[int] = (),
) -> GeneratorResult:
    context = build_context(store, spec, analyst_sections)
    result = call_structured(
        model=model,
        api_key=api_key,
        system=SYSTEM_PROMPT.format(schema=schema_hint(GeneratedSuite)),
        user=USER_TEMPLATE.format(
            key=spec.story_key,
            summary=spec.summary,
            scenarios=_scenarios_payload(spec),
            context="\n\n".join(h.content for h in context.hits),
        ),
        schema=GeneratedSuite,
        extra_check=_checker(spec),
        max_tokens=8000,
    )
    return GeneratorResult(suite=result.value, context=context, metrics=result.metrics)
