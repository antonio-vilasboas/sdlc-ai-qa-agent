"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-2: Bloqueio de acesso a utilizador com conta bloqueada

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-2`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_acesso_recusado_conta_bloqueada(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # Quando Introduzo o utilizador da conta bloqueada e a respetiva password
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então O acesso à loja é recusado
    expect(page.locator('[data-test="error"]')).to_be_visible()
    # E Permaneço na página de login (/)
    expect(page).to_have_url(BASE_URL + "/")
    # E Não sou redirecionado para a página de produtos
    expect(page.locator('[data-test="title"]')).to_have_count(0)


def test_c02_mensagem_conta_bloqueada(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # Quando Introduzo o utilizador da conta bloqueada e a respetiva password
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então É apresentada uma mensagem de erro
    expect(page.locator('[data-test="error"]')).to_be_visible()
    # E A mensagem indica que a conta se encontra bloqueada, com o texto exato 'Epic sadface: Sorry, this user has been locked out.'
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Sorry, this user has been locked out.")


def test_c03_fecho_mensagem_erro_conta_bloqueada(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # E Tentei autenticar-me com a conta bloqueada e a mensagem de erro de conta bloqueada está apresentada
    page.locator('[data-test="username"]').fill("locked_out_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="error"]')).to_be_visible()
    expect(page.locator('[data-test="error"]')).to_have_text("Epic sadface: Sorry, this user has been locked out.")
    # Quando Aciono o botão de fecho da mensagem de erro
    page.locator('[data-test="error-button"]').click()
    # Então A mensagem de erro deixa de estar visível
    expect(page.locator('[data-test="error"]')).to_have_count(0)
    # E Permaneço na página de login (/)
    expect(page).to_have_url(BASE_URL + "/")
