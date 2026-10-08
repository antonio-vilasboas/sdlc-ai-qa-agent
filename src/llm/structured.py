"""Chamadas ao LLM com saída estruturada e validada (LiteLLM + Pydantic).

Cada agente pede ao modelo uma resposta exclusivamente em JSON, que é validada contra um
modelo Pydantic. Se a resposta for inválida (JSON mal formado, campos em falta ou regras
de negócio violadas), o erro é devolvido ao modelo numa nova tentativa.

Cada chamada regista métricas (tokens, latência, custo) para a avaliação (métrica ET).
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Generic, TypeVar

import litellm
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

_JSON_BLOCK = re.compile(r"\{.*\}", re.S)


class LLMOutputError(Exception):
    """O modelo não produziu uma resposta válida dentro do número de tentativas."""


@dataclass
class CallMetrics:
    attempts: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float | None = 0.0
    errors: list[str] = field(default_factory=list)

    def add(self, prompt: int, completion: int, latency_ms: int, cost: float | None) -> None:
        self.attempts += 1
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.latency_ms += latency_ms
        self.cost_usd = None if cost is None or self.cost_usd is None else round(self.cost_usd + cost, 6)


@dataclass
class StructuredResult(Generic[T]):
    value: T
    metrics: CallMetrics


def _extract_json(text: str) -> str:
    """Aceita JSON puro ou envolvido em bloco de código Markdown."""
    match = _JSON_BLOCK.search(text)
    if not match:
        raise ValueError("a resposta não contém um objeto JSON")
    return match.group(0)


def call_structured(
    *,
    model: str,
    api_key: str,
    system: str,
    user: str,
    schema: type[T],
    extra_check: Callable[[T], list[str]] | None = None,
    max_attempts: int = 2,
    max_tokens: int = 4000,
) -> StructuredResult[T]:
    """Pede ao modelo um JSON conforme `schema`; valida e, se falhar, pede correção.

    `extra_check` permite validações de negócio além do esquema (devolve lista de erros).
    """
    messages: list[dict[str, str]] = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    metrics = CallMetrics()

    for _ in range(max_attempts):
        t0 = time.perf_counter()
        response = litellm.completion(
            model=model,
            api_key=api_key,
            messages=messages,
            temperature=0,
            max_tokens=max_tokens,
            num_retries=2,
            timeout=120,
        )
        latency = int((time.perf_counter() - t0) * 1000)
        try:
            cost: float | None = float(litellm.completion_cost(completion_response=response))
        except Exception:  # noqa: BLE001 — modelo sem tabela de preços no LiteLLM
            cost = None
        metrics.add(response.usage.prompt_tokens, response.usage.completion_tokens, latency, cost)

        raw = response.choices[0].message.content or ""
        try:
            value = schema.model_validate_json(_extract_json(raw))
            problems = extra_check(value) if extra_check else []
        except (ValueError, ValidationError) as exc:
            problems = [str(exc)[:1500]]
        if not problems:
            return StructuredResult(value=value, metrics=metrics)

        metrics.errors.extend(problems)
        messages += [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": "A resposta anterior tem os seguintes problemas. Corrige-os e devolve de novo "
                "APENAS o objeto JSON completo:\n- " + "\n- ".join(problems),
            },
        ]

    raise LLMOutputError(f"resposta inválida após {max_attempts} tentativas: {metrics.errors[-3:]}")


def schema_hint(schema: type[BaseModel]) -> str:
    """Esquema JSON compacto para incluir no prompt."""
    return json.dumps(schema.model_json_schema(), ensure_ascii=False)
