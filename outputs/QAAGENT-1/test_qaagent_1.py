"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-1: Autenticação de utilizador com credenciais válidas

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-1`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_login_valido(page: Page) -> None:
    # Dado O utilizador está na página de login da aplicação
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # Quando Introduz o utilizador válido no campo de utilizador
    page.locator('[data-test="username"]').fill("standard_user")
    # E Introduz a password correspondente no campo de password
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submete o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então O utilizador é redirecionado para a página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")


def test_c02_titulo_seccao_produtos_visivel(page: Page) -> None:
    # Dado O utilizador autenticou-se com credenciais válidas e está na página de catálogo
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Quando Observa o título da secção de produtos
    titulo = page.locator('[data-test="title"]')
    # Então O título da secção de produtos é visível
    expect(titulo).to_be_visible()
    # E O título apresentado é "Products"
    expect(titulo).to_have_text("Products")


def test_c03_lista_produtos_apresentada(page: Page) -> None:
    # Dado O utilizador autenticou-se com credenciais válidas e está na página de catálogo
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Quando Observa a lista de produtos disponíveis
    lista = page.locator('[data-test="inventory-list"]')
    # Então A lista de produtos é apresentada
    expect(lista).to_be_visible()
    # E A lista contém os 6 produtos disponíveis, com nome e preço
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(6)
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text([
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Bolt T-Shirt",
        "Sauce Labs Fleece Jacket",
        "Sauce Labs Onesie",
        "Test.allTheThings() T-Shirt (Red)",
    ])
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text([
        "$29.99",
        "$9.99",
        "$15.99",
        "$49.99",
        "$7.99",
        "$15.99",
    ])
