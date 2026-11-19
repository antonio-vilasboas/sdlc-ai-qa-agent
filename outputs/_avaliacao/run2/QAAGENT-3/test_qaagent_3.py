"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-3: Validação de campos obrigatórios no formulário de login

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-3`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_login_sem_campos_obrigatorios(page: Page) -> None:
    # Dado que o utilizador está na página de login
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # E que os campos de utilizador e password estão vazios
    expect(page.locator('[data-test="username"]')).to_have_value("")
    expect(page.locator('[data-test="password"]')).to_have_value("")
    # Quando o utilizador submete o formulário de login sem preencher nenhum campo
    page.locator('[data-test="login-button"]').click()
    # Então é apresentada a mensagem de erro "Epic sadface: Username is required"
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Username is required")
    # E o utilizador permanece na página de login
    expect(page).to_have_url(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()


def test_c02_login_sem_password(page: Page) -> None:
    # Dado que o utilizador está na página de login
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # E que o campo de password está vazio
    expect(page.locator('[data-test="password"]')).to_have_value("")
    # Quando o utilizador preenche apenas o campo de utilizador com "standard_user"
    page.locator('[data-test="username"]').fill("standard_user")
    expect(page.locator('[data-test="username"]')).to_have_value("standard_user")
    # E o utilizador submete o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então é apresentada a mensagem de erro "Epic sadface: Password is required"
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Password is required")
    # E o utilizador permanece na página de login
    expect(page).to_have_url(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
