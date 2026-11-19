"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-3: Validação de campos obrigatórios no formulário de login

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-3`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_login_sem_campos(page: Page) -> None:
    # Dado O utilizador está na página de login
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # Quando O utilizador submete o formulário de login sem preencher o utilizador nem a password
    page.locator('[data-test="login-button"]').click()
    # Então É apresentada a mensagem de erro indicando que o utilizador é obrigatório
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Username is required")
    # E A mensagem de erro não indica que a password é obrigatória
    expect(page.locator('[data-test="error"]')).not_to_contain_text("Password is required")
    # E O utilizador permanece na página de login
    expect(page).to_have_url(BASE_URL + "/")


def test_c02_login_so_utilizador(page: Page) -> None:
    # Dado O utilizador está na página de login
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # Quando O utilizador preenche o campo utilizador com 'standard_user'
    page.locator('[data-test="username"]').fill("standard_user")
    # E O utilizador deixa o campo password vazio
    expect(page.locator('[data-test="password"]')).to_have_value("")
    # E O utilizador submete o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então É apresentada a mensagem de erro indicando que a password é obrigatória
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Password is required")
    # E O utilizador permanece na página de login
    expect(page).to_have_url(BASE_URL + "/")
