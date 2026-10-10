"""Conversão determinística da especificação do Analista em Gherkin (português).

O Gherkin NÃO é gerado pelo LLM: é uma formatação direta dos cenários aprovados pelo
Analista. Assim, o texto que vai para o Xray (testes Cucumber) é exatamente o que foi
especificado, sem reescrita nem perda de rastreabilidade.
"""

from __future__ import annotations

from src.agents.models import AnalysisSpec, Scenario

_INDENT = "  "


_KEYWORDS = {
    "pt": ("Dado", "Quando", "Então", "E"),
    # O editor de testes Cucumber do Xray Cloud só reconhece as palavras-chave em inglês;
    # o texto dos passos mantém-se em português.
    "en": ("Given", "When", "Then", "And"),
}


def scenario_steps(sc: Scenario, keywords: str = "pt") -> list[str]:
    """Passos do cenário com as palavras-chave Gherkin em português (omissão) ou inglês."""
    given_kw, when_kw, then_kw, and_kw = _KEYWORDS[keywords]
    lines: list[str] = []
    for keyword, steps in ((given_kw, sc.given), (when_kw, sc.when), (then_kw, sc.then)):
        lines += [f"{keyword if i == 0 else and_kw} {step.strip().rstrip('.')}" for i, step in enumerate(steps)]
    return lines


def scenario_tags(story_key: str, sc: Scenario) -> list[str]:
    return [f"@{story_key}", f"@{sc.id}", *(f"@{r}" for r in sc.rules)]


def render_feature(spec: AnalysisSpec, title: str) -> str:
    """Ficheiro .feature completo (uma Funcionalidade, um Cenário por cenário do Analista)."""
    out = ["# language: pt", f"@{spec.story_key}", f"Funcionalidade: {title}", f"{_INDENT}{spec.summary}", ""]
    for sc in spec.scenarios:
        out.append(_INDENT + " ".join(scenario_tags(spec.story_key, sc)[1:]))
        out.append(f"{_INDENT}Cenário: {sc.id} – {sc.title}")
        out += [_INDENT * 2 + line for line in scenario_steps(sc)]
        out.append("")
    return "\n".join(out)
