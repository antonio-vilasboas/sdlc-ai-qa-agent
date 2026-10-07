"""Sanity check das integrações externas do SDLC AI QA Agent.

Valida, por esta ordem:
  1. Configuração (.env) — campos obrigatórios e formato.
  2. Jira Cloud REST API v3 — autenticação e acesso ao projeto.
  3. Confluence Cloud REST API v2 — autenticação e acesso ao espaço.
  4. Xray Cloud — autenticação OAuth2 (client credentials) e consulta GraphQL.
  5. LLM (Anthropic Claude via LiteLLM) — inferência mínima com contagem de tokens.

Uso:
    python scripts/sanity_check.py

Exit code 0 se todas as verificações passarem, 1 caso contrário.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable

import requests
from dotenv import dotenv_values
from pydantic import BaseModel, Field, HttpUrl, SecretStr, ValidationError, field_validator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HTTP_TIMEOUT_S: float = 15.0


# --------------------------------------------------------------------------- #
# Configuração
# --------------------------------------------------------------------------- #
class Settings(BaseModel):
    """Configuração carregada do .env e validada antes de qualquer chamada de rede."""

    atlassian_base_url: HttpUrl
    atlassian_user_email: str = Field(min_length=3, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    atlassian_api_token: SecretStr
    jira_project_key: str = Field(min_length=1, pattern=r"^[A-Z][A-Z0-9_]+$")
    confluence_space_key: str = Field(min_length=1)

    xray_client_id: SecretStr
    xray_client_secret: SecretStr
    xray_base_url: HttpUrl = Field(default="https://xray.cloud.getxray.app", validate_default=True)  # type: ignore[assignment]

    anthropic_api_key: SecretStr
    llm_model: str = "anthropic/claude-haiku-4-5-20251001"

    @field_validator("atlassian_api_token", "xray_client_id", "xray_client_secret", "anthropic_api_key")
    @classmethod
    def _not_blank(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("não pode estar vazio")
        return value

    @field_validator("llm_model")
    @classmethod
    def _anthropic_prefix(cls, value: str) -> str:
        if not value.startswith("anthropic/"):
            raise ValueError("deve usar o prefixo LiteLLM 'anthropic/' (ex.: anthropic/claude-haiku-4-5-20251001)")
        return value

    @property
    def atlassian_root(self) -> str:
        return str(self.atlassian_base_url).rstrip("/")

    @property
    def xray_root(self) -> str:
        return str(self.xray_base_url).rstrip("/")

    @property
    def atlassian_auth(self) -> tuple[str, str]:
        return (self.atlassian_user_email, self.atlassian_api_token.get_secret_value())


def load_settings(env_path: str = ".env") -> Settings:
    """Lê o .env (sem poluir os.environ) e normaliza as chaves para minúsculas."""
    raw = {k.lower(): v for k, v in dotenv_values(env_path).items() if v not in (None, "")}
    return Settings.model_validate(raw)


# --------------------------------------------------------------------------- #
# Infraestrutura HTTP
# --------------------------------------------------------------------------- #
def build_session() -> requests.Session:
    """Sessão HTTP com retries exponenciais para 429/5xx (respeita Retry-After)."""
    retry = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"Accept": "application/json"})
    return session


class CheckFailed(Exception):
    """Falha controlada de uma verificação, com mensagem pronta a mostrar."""


def _expect_ok(response: requests.Response, context: str) -> None:
    if response.ok:
        return
    hints: dict[int, str] = {
        401: "credenciais inválidas",
        403: "sem permissão",
        404: "recurso inexistente ou sem acesso",
    }
    hint = hints.get(response.status_code, "erro inesperado")
    raise CheckFailed(f"{context}: HTTP {response.status_code} ({hint}) — {response.text[:150]!r}")


# --------------------------------------------------------------------------- #
# Verificações
# --------------------------------------------------------------------------- #
class Status(str, Enum):
    OK = "✅"
    FAIL = "❌"


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: Status
    detail: str
    elapsed_ms: int


def check_jira(cfg: Settings, http: requests.Session) -> str:
    me = http.get(f"{cfg.atlassian_root}/rest/api/3/myself", auth=cfg.atlassian_auth, timeout=HTTP_TIMEOUT_S)
    _expect_ok(me, "Jira /myself")
    proj = http.get(
        f"{cfg.atlassian_root}/rest/api/3/project/{cfg.jira_project_key}",
        auth=cfg.atlassian_auth,
        timeout=HTTP_TIMEOUT_S,
    )
    _expect_ok(proj, f"Jira projeto '{cfg.jira_project_key}'")
    return f"utilizador '{me.json().get('displayName')}', projeto '{proj.json().get('name')}'"


def check_confluence(cfg: Settings, http: requests.Session) -> str:
    res = http.get(
        f"{cfg.atlassian_root}/wiki/api/v2/spaces",
        params={"keys": cfg.confluence_space_key, "limit": 1},
        auth=cfg.atlassian_auth,
        timeout=HTTP_TIMEOUT_S,
    )
    _expect_ok(res, "Confluence /spaces")
    results: list[dict[str, object]] = res.json().get("results", [])
    if not results:
        raise CheckFailed(f"espaço '{cfg.confluence_space_key}' não encontrado ou sem acesso")
    return f"espaço '{results[0].get('name')}' (id {results[0].get('id')})"


def check_xray(cfg: Settings, http: requests.Session) -> str:
    auth = http.post(
        f"{cfg.xray_root}/api/v2/authenticate",
        json={
            "client_id": cfg.xray_client_id.get_secret_value(),
            "client_secret": cfg.xray_client_secret.get_secret_value(),
        },
        timeout=HTTP_TIMEOUT_S,
    )
    _expect_ok(auth, "Xray OAuth2")
    token = auth.json()  # a API devolve o JWT como string JSON
    if not isinstance(token, str) or token.count(".") != 2:
        raise CheckFailed("Xray OAuth2: resposta não é um JWT válido")

    query = f'{{ getTests(jql: "project = {cfg.jira_project_key}", limit: 1) {{ total }} }}'
    gql = http.post(
        f"{cfg.xray_root}/api/v2/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {token}"},
        timeout=HTTP_TIMEOUT_S,
    )
    _expect_ok(gql, "Xray GraphQL")
    payload: dict[str, object] = gql.json()
    if payload.get("errors"):
        raise CheckFailed(f"Xray GraphQL: {payload['errors']}")
    total = payload["data"]["getTests"]["total"]  # type: ignore[index]
    return f"token OAuth2 obtido, {total} Test(s) no projeto"


def check_llm(cfg: Settings, _http: requests.Session) -> str:
    import litellm  # import tardio: evita o custo de arranque se a config falhar antes

    response = litellm.completion(
        model=cfg.llm_model,
        api_key=cfg.anthropic_api_key.get_secret_value(),
        messages=[{"role": "user", "content": "Responde apenas com a palavra: OK"}],
        max_tokens=10,
        timeout=HTTP_TIMEOUT_S * 2,
        num_retries=2,
    )
    reply = (response.choices[0].message.content or "").strip()
    usage = response.usage
    return f"modelo '{cfg.llm_model}', resposta '{reply}', tokens in/out {usage.prompt_tokens}/{usage.completion_tokens}"


CHECKS: tuple[tuple[str, Callable[[Settings, requests.Session], str]], ...] = (
    ("Jira Cloud", check_jira),
    ("Confluence Cloud", check_confluence),
    ("Xray Cloud", check_xray),
    ("LLM (Claude)", check_llm),
)


def run_check(name: str, fn: Callable[[Settings, requests.Session], str], cfg: Settings, http: requests.Session) -> CheckResult:
    start = time.perf_counter()
    try:
        detail, status = fn(cfg, http), Status.OK
    except CheckFailed as exc:
        detail, status = str(exc), Status.FAIL
    except requests.RequestException as exc:
        detail, status = f"erro de rede: {exc.__class__.__name__}: {exc}", Status.FAIL
    except Exception as exc:  # noqa: BLE001 — fronteira do script: reportar e continuar
        detail, status = f"{exc.__class__.__name__}: {exc}", Status.FAIL
    return CheckResult(name, status, detail, int((time.perf_counter() - start) * 1000))


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
def main() -> int:
    line = "=" * 72
    print(f"{line}\nSANITY CHECK — SDLC AI QA AGENT\n{line}")

    try:
        cfg = load_settings()
    except ValidationError as exc:
        print("\n❌ Configuração inválida no .env:")
        for err in exc.errors():
            field = ".".join(str(p) for p in err["loc"]).upper()
            print(f"   - {field}: {err['msg']}")
        return 1
    print("\n✅ Configuração (.env) válida")

    http = build_session()
    results = [run_check(name, fn, cfg, http) for name, fn in CHECKS]

    for idx, r in enumerate(results, start=1):
        print(f"\n[{idx}/{len(results)}] {r.status.value} {r.name} ({r.elapsed_ms} ms)\n      {r.detail}")

    failed = [r for r in results if r.status is Status.FAIL]
    print(f"\n{line}")
    if failed:
        print(f"FALHAS: {len(failed)}/{len(results)} — {', '.join(r.name for r in failed)}")
        return 1
    print(f"TODAS AS {len(results)} INTEGRAÇÕES VALIDADAS COM SUCESSO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
