"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-2: Bloqueio de acesso a utilizador com conta bloqueada

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-2`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_acesso_recusado_conta_bloqueada(page: Page) -> None:
    # Dado Estou na página de login da loja
    page.goto(BASE_URL + "/")
    # Quando Introduzo o utilizador de teste de conta bloqueada e a password de teste
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então O acesso à loja é recusado
    expect(page.locator('[data-test="error"]')).to_be_visible()
    # E Permaneço na página de login (/)
    expect(page).to_have_url(BASE_URL + "/")
    # E Não sou redirecionado para o catálogo de produtos
    expect(page).not_to_have_url(BASE_URL + "/inventory.html")


def test_c02_mensagem_conta_bloqueada_login(page: Page) -> None:
    # Dado Estou na página de login da loja
    page.goto(BASE_URL + "/")
    # Quando Introduzo o utilizador de teste de conta bloqueada e a password de teste
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então É apresentada uma mensagem de erro
    expect(page.locator('[data-test="error"]')).to_be_visible()
    # E A mensagem de erro apresentada é exatamente "Epic sadface: Sorry, this user has been locked out."
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Sorry, this user has been locked out.")
    # E Permaneço na página de login
    expect(page).to_have_url(BASE_URL + "/")


def test_c03_fecho_mensagem_conta_bloqueada(page: Page) -> None:
    # Dado Estou na página de login da loja
    page.goto(BASE_URL + "/")
    # E Tentei iniciar sessão com o utilizador de teste de conta bloqueada e a password de teste
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    # E A mensagem de conta bloqueada está apresentada
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Sorry, this user has been locked out.")
    # Quando Fecho a mensagem de erro através do botão de fecho
    page.locator('[data-test="error-button"]').click()
    # Então A mensagem de erro deixa de ser apresentada
    expect(page.locator('[data-test="error"]')).to_have_count(0)
    # E Permaneço na página de login
    expect(page).to_have_url(BASE_URL + "/")
