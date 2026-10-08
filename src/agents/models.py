"""Contratos de dados trocados entre agentes (validados com Pydantic).

Os agentes não comunicam por texto livre: cada um produz um objeto com esquema fixo,
o que torna a passagem de dados entre etapas previsível e verificável (RNF03).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Scenario(BaseModel):
    """Um cenário de teste em linguagem de negócio (sem seletores nem código)."""

    id: str = Field(pattern=r"^C\d{2}$", description="Identificador sequencial: C01, C02, ...")
    title: str = Field(min_length=5, description="Título curto do cenário, em português")
    type: Literal["nominal", "exceção", "validação"] = Field(
        description="nominal = caminho de sucesso; exceção = erro de negócio; validação = campo obrigatório/formato"
    )
    given: list[str] = Field(min_length=1, description="Passos 'Dado' (pré-condições)")
    when: list[str] = Field(min_length=1, description="Passos 'Quando' (ações do utilizador)")
    then: list[str] = Field(min_length=1, description="Passos 'Então' (resultados observáveis a verificar)")
    rules: list[str] = Field(min_length=1, description="IDs das regras de negócio verificadas (ex.: RN-LOGIN-02)")
    criteria: list[int] = Field(min_length=1, description="Números dos critérios de aceitação da User Story cobertos")
    test_data: dict[str, str] = Field(
        default_factory=dict,
        description="Dados concretos retirados do contexto (ex.: utilizador, password, texto exato esperado)",
    )


class AnalysisSpec(BaseModel):
    """Saída do Agente Analista: o que deve ser testado para uma User Story."""

    story_key: str = Field(pattern=r"^[A-Z][A-Z0-9]+-\d+$")
    summary: str = Field(description="Uma frase com o objetivo dos testes")
    scenarios: list[Scenario] = Field(min_length=1)
    gaps: list[str] = Field(
        default_factory=list,
        description="Informação necessária que não existe na User Story nem no contexto (nunca inventar)",
    )


class GeneratedTest(BaseModel):
    """Uma função de teste Playwright (pytest) correspondente a um cenário do Analista."""

    scenario_id: str = Field(pattern=r"^C\d{2}$", description="ID do cenário implementado (C01, C02, ...)")
    function_name: str = Field(
        pattern=r"^test_c\d{2}_[a-z0-9_]+$",
        description="Nome da função: test_<id em minúsculas>_<descrição curta em snake_case>",
    )
    code: str = Field(min_length=20, description="Código Python completo da função (def ...), sem imports")


class GeneratedSuite(BaseModel):
    """Saída do Agente Gerador: implementação Playwright dos cenários de uma User Story."""

    story_key: str = Field(pattern=r"^[A-Z][A-Z0-9]+-\d+$")
    tests: list[GeneratedTest] = Field(min_length=1)
    assumptions: list[str] = Field(
        default_factory=list,
        description="Valores de exemplo usados que não constam do contexto (ex.: nome, apelido, código postal)",
    )
