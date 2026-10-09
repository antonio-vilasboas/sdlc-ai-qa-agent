"""Testes unitários do Agente Validador (sem browser, sem LLM, sem rede).

Executar: pytest tests/unit -v
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.agents.validator import allowed_selectors, validate  # noqa: E402

KB = (ROOT / "knowledge" / "swaglabs_knowledge_base.md").read_text(encoding="utf-8")
ALLOWED = allowed_selectors([KB])

HEADER = '''import re

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"
'''

GOOD = HEADER + '''

def test_c01_login_valido(page: Page) -> None:
    # Dado O utilizador está na página de login
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    # Então É apresentado o catálogo
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
'''


def _rules(code: str, scenarios: tuple[str, ...] = ("C01",)) -> set[str]:
    return {i.rule for i in validate(code, ALLOWED, scenarios).errors}


def test_lista_de_seletores_expande_padroes_por_produto() -> None:
    assert {"username", "checkout", "shopping-cart-badge", "complete-header"} <= ALLOWED
    assert "add-to-cart-sauce-labs-backpack" in ALLOWED
    assert "remove-sauce-labs-bike-light" in ALLOWED
    assert "add-to-cart-test.allthethings()-t-shirt-(red)" in ALLOWED  # sem normalização
    assert not any("<produto>" in s for s in ALLOWED)


def test_codigo_correto_e_aprovado() -> None:
    report = validate(GOOD, ALLOWED, ["C01"])
    assert report.approved, report.issues
    assert report.selectors_used == ["login-button", "password", "title", "username"]
    assert report.expects_per_test == {"test_c01_login_valido": 1}


def test_v1_erro_de_sintaxe() -> None:
    assert _rules(GOOD.replace('.click()', '.click(')) == {"V1"}


def test_v2_importacao_nao_permitida() -> None:
    assert "V2" in _rules("import os\n" + GOOD)


def test_v3_espera_fixa() -> None:
    code = GOOD.replace("    # Então", "    page.wait_for_timeout(2000)\n    # Então")
    assert _rules(code) == {"V3"}


def test_v4_seletor_inventado() -> None:
    code = GOOD.replace('"login-button"', '"login-btn"')
    assert _rules(code) == {"V4"}


def test_v4_seletor_fora_da_convencao() -> None:
    assert _rules(GOOD.replace("'[data-test=\"username\"]'", "'#user-name'")) == {"V4"}
    assert _rules(GOOD.replace("page.locator('[data-test=\"password\"]')", "page.get_by_role('textbox')")) == {"V4"}


def test_v5_sem_asercoes() -> None:
    code = GOOD.replace("    expect(page.locator('[data-test=\"title\"]')).to_have_text(\"Products\")\n", "")
    assert _rules(code) == {"V5"}


def test_v6_cenario_sem_teste() -> None:
    assert _rules(GOOD, ("C01", "C02")) == {"V6"}


def test_v7_teste_sem_goto_e_apenas_aviso() -> None:
    code = GOOD.replace('    page.goto(BASE_URL + "/")\n', "")
    report = validate(code, ALLOWED, ["C01"])
    assert report.approved
    assert [w.rule for w in report.warnings] == ["V7"]
