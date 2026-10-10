"""Registo dos testes gerados no Xray Cloud e ligação à User Story no Jira.

- Xray Cloud: autenticação OAuth2 (client credentials) e API GraphQL, para criar testes do
  tipo Cucumber com a definição Gherkin e para a atualizar em execuções seguintes.
- Jira Cloud (REST v3): pesquisa por etiqueta (idempotência) e ligação "tests / is tested by"
  entre o teste e a User Story, que é o que o Xray usa para calcular a cobertura.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

HTTP_TIMEOUT_S = 30

_CREATE_TEST = """
mutation CreateTest($testType: UpdateTestTypeInput, $gherkin: String, $jira: JSON!) {
  createTest(testType: $testType, gherkin: $gherkin, jira: $jira) {
    test { issueId jira(fields: ["key"]) }
    warnings
  }
}"""

_UPDATE_GHERKIN = """
mutation UpdateGherkin($issueId: String!, $gherkin: String!) {
  updateGherkinTestDefinition(issueId: $issueId, gherkin: $gherkin) { issueId }
}"""


class XrayError(Exception):
    """Falha numa chamada ao Xray ou ao Jira, com mensagem pronta a mostrar."""


@dataclass(frozen=True)
class IssueRef:
    issue_id: str
    key: str


def _ok(response: requests.Response, context: str) -> Any:
    if not response.ok:
        raise XrayError(f"{context}: HTTP {response.status_code} — {response.text[:300]}")
    return response.json() if response.content else None


class XrayClient:
    def __init__(self, http: requests.Session, root: str, client_id: str, client_secret: str) -> None:
        self._http = http
        self._root = root.rstrip("/")
        self._credentials = {"client_id": client_id, "client_secret": client_secret}
        self._token: str | None = None

    @property
    def token(self) -> str:
        if self._token is None:
            token = _ok(self._http.post(f"{self._root}/api/v2/authenticate", json=self._credentials,
                                        timeout=HTTP_TIMEOUT_S), "Xray OAuth2")
            if not isinstance(token, str):
                raise XrayError("Xray OAuth2: resposta sem token")
            self._token = token
        return self._token

    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        payload = _ok(self._http.post(f"{self._root}/api/v2/graphql",
                                      json={"query": query, "variables": variables},
                                      headers={"Authorization": f"Bearer {self.token}"},
                                      timeout=HTTP_TIMEOUT_S), "Xray GraphQL")
        if payload.get("errors"):
            raise XrayError(f"Xray GraphQL: {payload['errors']}")
        return payload["data"]

    def create_cucumber_test(self, project_key: str, summary: str, labels: list[str], gherkin: str) -> IssueRef:
        data = self.graphql(_CREATE_TEST, {
            "testType": {"name": "Cucumber"},
            "gherkin": gherkin,
            "jira": {"fields": {"project": {"key": project_key}, "summary": summary, "labels": labels}},
        })["createTest"]
        test = data["test"]
        return IssueRef(issue_id=str(test["issueId"]), key=test["jira"]["key"])

    def update_gherkin(self, issue_id: str, gherkin: str) -> None:
        self.graphql(_UPDATE_GHERKIN, {"issueId": issue_id, "gherkin": gherkin})


class JiraLinks:
    """Operações no Jira necessárias à rastreabilidade (pesquisa, atualização e ligação)."""

    def __init__(self, http: requests.Session, root: str, auth: tuple[str, str]) -> None:
        self._http = http
        self._root = root.rstrip("/")
        self._auth = auth

    def find_by_label(self, project_key: str, label: str) -> IssueRef | None:
        data = _ok(self._http.get(f"{self._root}/rest/api/3/search/jql", auth=self._auth, timeout=HTTP_TIMEOUT_S,
                                  params={"jql": f'project = "{project_key}" AND labels = "{label}"',
                                          "fields": "summary", "maxResults": 2}), f"Jira pesquisa {label}")
        issues = data.get("issues", [])
        if len(issues) > 1:
            raise XrayError(f"mais do que um item com a etiqueta {label}: corrigir no Jira")
        return IssueRef(issue_id=str(issues[0]["id"]), key=issues[0]["key"]) if issues else None

    def keys_by_labels(self, project_key: str, labels: list[str]) -> list[str]:
        """Chaves dos itens que têm todas as etiquetas indicadas."""
        jql = f'project = "{project_key}"' + "".join(f' AND labels = "{lb}"' for lb in labels)
        data = _ok(self._http.get(f"{self._root}/rest/api/3/search/jql", auth=self._auth, timeout=HTTP_TIMEOUT_S,
                                  params={"jql": jql, "fields": "summary", "maxResults": 100}), "Jira pesquisa")
        return [i["key"] for i in data.get("issues", [])]

    def update_summary(self, key: str, summary: str) -> None:
        _ok(self._http.put(f"{self._root}/rest/api/3/issue/{key}", auth=self._auth, timeout=HTTP_TIMEOUT_S,
                           json={"fields": {"summary": summary}}), f"Jira atualizar {key}")

    def test_link_type(self) -> str:
        """Nome do tipo de ligação "tests / is tested by" criado pelo Xray."""
        data = _ok(self._http.get(f"{self._root}/rest/api/3/issueLinkType", auth=self._auth,
                                  timeout=HTTP_TIMEOUT_S), "Jira tipos de ligação")
        for t in data.get("issueLinkTypes", []):
            if t.get("outward", "").lower() == "tests" and t.get("inward", "").lower() == "is tested by":
                return str(t["name"])
        raise XrayError('tipo de ligação "tests / is tested by" não encontrado (criado pelo Xray na instalação)')

    def _links(self, test_key: str) -> list[dict[str, Any]]:
        data = _ok(self._http.get(f"{self._root}/rest/api/3/issue/{test_key}", auth=self._auth,
                                  timeout=HTTP_TIMEOUT_S, params={"fields": "issuelinks"}), f"Jira {test_key}")
        return list(data["fields"].get("issuelinks", []))

    def link_direction(self, test_key: str, story_key: str, link_type: str) -> str | None:
        """Vista a partir do teste: "ok" se <teste> tests <story>; "invertida" se ao contrário; None se não há."""
        for link in self._links(test_key):
            if link["type"]["name"] != link_type:
                continue
            if link.get("outwardIssue", {}).get("key") == story_key:
                return "ok"
            if link.get("inwardIssue", {}).get("key") == story_key:
                return "invertida"
        return None

    def _create_link(self, inward: str, outward: str, link_type: str) -> None:
        _ok(self._http.post(f"{self._root}/rest/api/3/issueLink", auth=self._auth, timeout=HTTP_TIMEOUT_S, json={
            "type": {"name": link_type}, "inwardIssue": {"key": inward}, "outwardIssue": {"key": outward},
        }), f"Jira ligar {inward} ↔ {outward}")

    def _delete_link(self, test_key: str, story_key: str, link_type: str) -> None:
        for link in self._links(test_key):
            other = link.get("inwardIssue", link.get("outwardIssue", {})).get("key")
            if link["type"]["name"] == link_type and other == story_key:
                _ok(self._http.delete(f"{self._root}/rest/api/3/issueLink/{link['id']}", auth=self._auth,
                                      timeout=HTTP_TIMEOUT_S), f"Jira remover ligação {link['id']}")

    def link_test_to_story(self, test_key: str, story_key: str, link_type: str) -> str:
        """Garante "<teste> tests <story>" (na User Story: "is tested by <teste>").

        A semântica de inwardIssue/outwardIssue na API do Jira é ambígua, por isso o sentido
        é confirmado depois de criar a ligação e corrigido se ficar invertido.
        Devolve "existente", "criada" ou "corrigida".
        """
        current = self.link_direction(test_key, story_key, link_type)
        if current == "ok":
            return "existente"
        if current == "invertida":
            self._delete_link(test_key, story_key, link_type)
        self._create_link(inward=story_key, outward=test_key, link_type=link_type)
        if self.link_direction(test_key, story_key, link_type) == "ok":
            return "criada" if current is None else "corrigida"
        self._delete_link(test_key, story_key, link_type)
        self._create_link(inward=test_key, outward=story_key, link_type=link_type)
        if self.link_direction(test_key, story_key, link_type) != "ok":
            raise XrayError(f"não foi possível ligar {test_key} → {story_key} no sentido correto")
        return "criada"
