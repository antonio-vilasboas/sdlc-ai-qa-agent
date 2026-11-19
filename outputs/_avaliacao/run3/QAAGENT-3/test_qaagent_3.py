"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-3: Validação de campos obrigatórios no formulário de login

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-3`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_submeter_login_sem_campos(page: Page) -> None:
    # Dado O utilizador está na página de login
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # Quando O utilizador submete o formulário de login sem preencher o utilizador nem a password
    page.locator('[data-test="login-button"]').click()
    # Então É apresentada a mensagem de erro "Epic sadface: Username is required"
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Username is required")
    # E O utilizador permanece na página de login
    expect(page).to_have_url(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()


def test_c02_submeter_login_apenas_utilizador(page: Page) -> None:
    # Dado O utilizador está na página de login
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # Quando O utilizador preenche o campo utilizador com "standard_user"
    page.locator('[data-test="username"]').fill("standard_user")
    expect(page.locator('[data-test="username"]')).to_have_value("standard_user")
    # E O utilizador submete o formulário de login sem preencher a password
    page.locator('[data-test="login-button"]').click()
    # Então É apresentada a mensagem de erro "Epic sadface: Password is required"
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Password is required")
    # E O utilizador permanece na página de login
    expect(page).to_have_url(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
