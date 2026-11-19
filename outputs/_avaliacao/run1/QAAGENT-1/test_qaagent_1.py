"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-1: Autenticação de utilizador com credenciais válidas

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-1`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_login_valido_redireciona_catalogo(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # Quando Introduzo o utilizador válido standard_user
    page.locator('[data-test="username"]').fill("standard_user")
    # E Introduzo a password secret_sauce
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então Sou redirecionado para a página de catálogo de produtos (/inventory.html)
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O utilizador deixa de ver a página de login
    expect(page.locator('[data-test="login-button"]')).to_have_count(0)


def test_c02_titulo_produtos_visivel_apos_login(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # Quando Introduzo o utilizador válido standard_user
    page.locator('[data-test="username"]').fill("standard_user")
    # E Introduzo a password secret_sauce
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # E Chego à página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Então O título da página de catálogo é visível com o texto "Products"
    expect(page.locator('[data-test="title"]')).to_be_visible()
    expect(page.locator('[data-test="title"]')).to_have_text("Products")


def test_c03_lista_produtos_disponiveis_apos_login(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # Quando Introduzo o utilizador válido standard_user
    page.locator('[data-test="username"]').fill("standard_user")
    # E Introduzo a password secret_sauce
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # E Chego à página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Então É apresentada a lista de produtos com 6 produtos
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(6)
    # E Cada produto apresenta nome e preço
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_count(6)
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_count(6)
    # E Os produtos apresentados são: Sauce Labs Backpack ($29.99), Sauce Labs Bike Light ($9.99), Sauce Labs Bolt T-Shirt ($15.99), Sauce Labs Fleece Jacket ($49.99), Sauce Labs Onesie ($7.99) e Test.allTheThings() T-Shirt (Red) ($15.99)
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text(["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Bolt T-Shirt", "Sauce Labs Fleece Jacket", "Sauce Labs Onesie", "Test.allTheThings() T-Shirt (Red)"])
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text(["$29.99", "$9.99", "$15.99", "$49.99", "$7.99", "$15.99"])
