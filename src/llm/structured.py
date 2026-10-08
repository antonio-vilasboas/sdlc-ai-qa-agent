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

litellm.suppress_debug_info = True  # sem mensagens "Give Feedback / Get Help" no terminal

# Modelos que rejeitam o parâmetro temperature (ex.: gerações recentes do Claude).
# Preenchido automaticamente à primeira rejeição, para não repetir o erro.
_NO_TEMPERATURE: set[str] = set()

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
    finish_reasons: list[str] = field(default_factory=list)  # "stop" = completa; "length" = truncada

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
        response = _complete(model=model, api_key=api_key, messages=messages, max_tokens=max_tokens)
        latency = int((time.perf_counter() - t0) * 1000)
        try:
            cost: float | None = float(litellm.completion_cost(completion_response=response))
        except Exception:  # noqa: BLE001 — modelo sem tabela de preços no LiteLLM
            cost = None
        metrics.add(response.usage.prompt_tokens, response.usage.completion_tokens, latency, cost)

        choice = response.choices[0]
        finish = str(getattr(choice, "finish_reason", "") or "")
        metrics.finish_reasons.append(finish)
        raw = choice.message.content or ""
        if finish == "length":
            # Resposta cortada pelo limite de tokens: o JSON fica incompleto. Pede-se uma versão
            # mais compacta em vez de reportar um erro de sintaxe enganador.
            problems = [
                f"a resposta foi truncada ao atingir o limite de {max_tokens} tokens; "
                "devolve o objeto JSON completo de forma mais compacta (sem texto nem comentários supérfluos)"
            ]
        else:
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


def _complete(*, model: str, api_key: str, messages: list[dict[str, str]], max_tokens: int):  # type: ignore[no-untyped-def]
    """Pedido ao modelo com temperature=0 (respostas o mais deterministas possível).

    Se o modelo rejeitar o parâmetro, repete sem ele e memoriza a rejeição.
    Repetições automáticas apenas para erros transitórios (limite de pedidos, servidor).
    """
    kwargs = {"model": model, "api_key": api_key, "messages": messages, "max_tokens": max_tokens, "timeout": 120}
    if model not in _NO_TEMPERATURE:
        try:
            return litellm.completion(**kwargs, temperature=0, num_retries=0)
        except litellm.BadRequestError as exc:
            if "temperature" not in str(exc):
                raise
            _NO_TEMPERATURE.add(model)
    return litellm.completion(**kwargs, num_retries=2)


def temperature_supported(model: str) -> bool:
    return model not in _NO_TEMPERATURE


def schema_hint(schema: type[BaseModel]) -> str:
    """Esquema JSON compacto para incluir no prompt."""
    return json.dumps(schema.model_json_schema(), ensure_ascii=False)
