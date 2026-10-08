"""Agente Validador de Testes (determinístico, sem LLM).

Analisa estaticamente o módulo pytest/Playwright produzido pelo Gerador, através da
árvore sintática do Python (módulo `ast`), sem executar o código nem abrir o browser.

Regras verificadas (identificadores usados no relatório e no feedback ao Gerador):
  V1  sintaxe       o módulo é Python válido
  V2  importações   apenas `re` e `playwright.sync_api` (Page, expect)
  V3  proibidos     sem esperas fixas (time.sleep, wait_for_timeout) nem eval/exec/open
  V4  seletores     só page.locator('[data-test="..."]') com valores existentes na base de
                    conhecimento; sem XPath, CSS, get_by_role, get_by_text, etc.
  V5  asserções     cada teste tem pelo menos uma asserção expect(...)
  V6  cobertura     uma função de teste por cenário do Analista
  V7  independência cada teste começa com page.goto(...) (aviso)

O Validador não usa o modelo de linguagem: quem gera o código não é quem o avalia.
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel, Field

ALLOWED_IMPORTS: dict[str, set[str]] = {"re": set(), "playwright.sync_api": {"Page", "expect"}}
FORBIDDEN_CALLS = {"sleep", "wait_for_timeout", "eval", "exec", "open", "__import__"}
FORBIDDEN_LOCATORS = {
    "get_by_role", "get_by_text", "get_by_label", "get_by_placeholder", "get_by_alt_text",
    "get_by_title", "get_by_test_id", "query_selector", "query_selector_all", "wait_for_selector",
    "click", "fill", "type", "check", "select_option", "hover", "press", "dblclick",
}  # métodos de page que recebem seletor diretamente (devem passar por page.locator)
_SELECTOR = re.compile(r'^\[data-test="([^"]+)"\]$')
_BACKTICK = re.compile(r"`([^`]+)`")
_PATTERN = "<produto>"


class Issue(BaseModel):
    rule: Literal["V1", "V2", "V3", "V4", "V5", "V6", "V7"]
    severity: Literal["erro", "aviso"]
    test: str | None = Field(default=None, description="função de teste afetada")
    line: int | None = None
    message: str

    def __str__(self) -> str:
        where = f"{self.test or 'módulo'}" + (f", linha {self.line}" if self.line else "")
        return f"[{self.rule}] {where}: {self.message}"


class ValidationReport(BaseModel):
    approved: bool
    tests: list[str]
    selectors_used: list[str]
    expects_per_test: dict[str, int]
    issues: list[Issue]

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "erro"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "aviso"]


# -- lista de seletores permitidos -----------------------------------------------------
def allowed_selectors(section_texts: Iterable[str]) -> set[str]:
    """Extrai os valores data-test documentados nas tabelas da base de conhecimento.

    Os padrões com <produto> (ex.: add-to-cart-<produto>) são expandidos com os sufixos
    da tabela de produtos, exatamente como escritos (sem normalizar).
    """
    selectors: set[str] = set()
    suffixes: set[str] = set()
    for text in section_texts:
        col_selector: int | None = None
        col_suffix: int | None = None
        for line in text.splitlines():
            if not line.startswith("|"):
                col_selector = col_suffix = None
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if "data-test" in cells:
                col_selector = cells.index("data-test")
                continue
            header_suffix = next((i for i, c in enumerate(cells) if c.startswith("Sufixo")), None)
            if header_suffix is not None:
                col_suffix = header_suffix
                continue
            if col_selector is not None and col_selector < len(cells):
                selectors.update(_BACKTICK.findall(cells[col_selector]))
            if col_suffix is not None and col_suffix < len(cells):
                suffixes.update(_BACKTICK.findall(cells[col_suffix]))

    expanded = {s for s in selectors if _PATTERN not in s}
    for pattern in (s for s in selectors if _PATTERN in s):
        expanded.update(pattern.replace(_PATTERN, suffix) for suffix in suffixes)
    return expanded


# -- análise ---------------------------------------------------------------------------
def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def _is_page_method(node: ast.Call, name: str) -> bool:
    f = node.func
    return isinstance(f, ast.Attribute) and f.attr == name and isinstance(f.value, ast.Name) and f.value.id == "page"


def _check_imports(tree: ast.Module) -> list[Issue]:
    issues: list[Issue] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in ALLOWED_IMPORTS:
                    issues.append(Issue(rule="V2", severity="erro", line=node.lineno,
                                        message=f"importação não permitida: {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            allowed = ALLOWED_IMPORTS.get(node.module or "")
            names = {a.name for a in node.names}
            if allowed is None or not names <= allowed:
                issues.append(Issue(rule="V2", severity="erro", line=node.lineno,
                                    message=f"importação não permitida: from {node.module} import {', '.join(sorted(names))}"))
    return issues


def _check_function(fn: ast.FunctionDef, allowed: set[str]) -> tuple[list[Issue], list[str], int]:
    issues: list[Issue] = []
    used: list[str] = []
    expects = 0
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name in FORBIDDEN_CALLS:
            issues.append(Issue(rule="V3", severity="erro", test=fn.name, line=node.lineno,
                                message=f"chamada proibida: {name}() (o Playwright espera automaticamente pelos elementos)"
                                if name in ("sleep", "wait_for_timeout") else f"chamada proibida: {name}()"))
        elif name == "expect":
            expects += 1
        elif _is_page_method(node, "locator"):
            arg = node.args[0] if node.args else None
            if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                issues.append(Issue(rule="V4", severity="erro", test=fn.name, line=node.lineno,
                                    message="o seletor tem de ser um texto literal [data-test=\"...\"]"))
                continue
            match = _SELECTOR.match(arg.value)
            if not match:
                issues.append(Issue(rule="V4", severity="erro", test=fn.name, line=node.lineno,
                                    message=f"seletor fora da convenção data-test: {arg.value!r}"))
            elif match.group(1) not in allowed:
                issues.append(Issue(rule="V4", severity="erro", test=fn.name, line=node.lineno,
                                    message=f"seletor inexistente na base de conhecimento: {match.group(1)!r}"))
            else:
                used.append(match.group(1))
        elif name in FORBIDDEN_LOCATORS and isinstance(node.func, ast.Attribute) \
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "page":
            issues.append(Issue(rule="V4", severity="erro", test=fn.name, line=node.lineno,
                                message=f"page.{name}() não é permitido; usar page.locator('[data-test=\"...\"]')"))

    if expects == 0:
        issues.append(Issue(rule="V5", severity="erro", test=fn.name, line=fn.lineno,
                            message="o teste não tem nenhuma asserção expect(...)"))
    first = fn.body[0] if fn.body else None
    starts_with_goto = (
        isinstance(first, ast.Expr) and isinstance(first.value, ast.Call) and _is_page_method(first.value, "goto")
    )
    if not starts_with_goto:
        issues.append(Issue(rule="V7", severity="aviso", test=fn.name, line=fn.lineno,
                            message="o teste não começa com page.goto(...): pode depender do estado de outro teste"))
    return issues, used, expects


def validate(code: str, allowed: set[str], scenario_ids: Iterable[str]) -> ValidationReport:
    """Valida o módulo de testes. Aprovado = nenhum erro (os avisos não bloqueiam)."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        issue = Issue(rule="V1", severity="erro", line=exc.lineno, message=f"erro de sintaxe: {exc.msg}")
        return ValidationReport(approved=False, tests=[], selectors_used=[], expects_per_test={}, issues=[issue])

    issues = _check_imports(tree)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    used: list[str] = []
    expects: dict[str, int] = {}
    for fn in functions:
        fn_issues, fn_used, n_expect = _check_function(fn, allowed)
        issues += fn_issues
        used += fn_used
        expects[fn.name] = n_expect

    expected = sorted(s.lower() for s in scenario_ids)
    found = sorted(fn.name.split("_")[1] for fn in functions if fn.name.count("_") >= 2)
    if found != expected:
        issues.append(Issue(rule="V6", severity="erro",
                            message=f"esperada uma função por cenário {expected}; encontradas {found}"))

    return ValidationReport(
        approved=not any(i.severity == "erro" for i in issues),
        tests=[fn.name for fn in functions],
        selectors_used=sorted(set(used)),
        expects_per_test=expects,
        issues=issues,
    )
