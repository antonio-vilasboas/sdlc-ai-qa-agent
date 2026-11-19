"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-2: Bloqueio de acesso a utilizador com conta bloqueada

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-2`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_acesso_recusado_conta_bloqueada(page: Page) -> None:
    # Dado Que estou na página de login da loja
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # Quando Introduzo o utilizador de uma conta bloqueada e a respetiva password
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então O acesso à loja é recusado
    expect(page.locator('[data-test="error"]')).to_be_visible()
    expect(page).not_to_have_url(BASE_URL + "/inventory.html")
    # E Permaneço na página de login
    expect(page).to_have_url(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()


def test_c02_mensagem_erro_conta_bloqueada(page: Page) -> None:
    # Dado Que estou na página de login da loja
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # Quando Introduzo o utilizador de uma conta bloqueada e a respetiva password
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então É apresentada uma mensagem de erro com o texto 'Epic sadface: Sorry, this user has been locked out.'
    expect(page.locator('[data-test="error"]')).to_be_visible()
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Sorry, this user has been locked out.")


def test_c03_fecho_mensagem_conta_bloqueada(page: Page) -> None:
    # Dado Que estou na página de login da loja
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # E Que a mensagem de erro de conta bloqueada está apresentada após uma tentativa de login com a conta bloqueada
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Sorry, this user has been locked out.")
    # Quando Utilizo o botão de fechar a mensagem de erro
    page.locator('[data-test="error-button"]').click()
    # Então A mensagem de erro deixa de ser apresentada
    expect(page.locator('[data-test="error"]')).to_have_count(0)
    # E Permaneço na página de login
    expect(page).to_have_url(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
