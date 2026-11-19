"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-1: Autenticação de utilizador com credenciais válidas

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-1`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_login_valido(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # Quando Introduzo o utilizador válido e a respetiva password
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então Sou redirecionado para a página de catálogo de produtos
    expect(page.locator('[data-test="product-sort-container"]')).to_be_visible()
    # E O endereço da página de destino é /inventory.html
    expect(page).to_have_url(BASE_URL + "/inventory.html")


def test_c02_titulo_produtos_visivel_apos_login(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # Quando Efetuo login com um utilizador válido e a respetiva password
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    # Então Na página de catálogo, o título da secção de produtos está visível
    expect(page.locator('[data-test="title"]')).to_be_visible()
    # E O título apresentado é "Products"
    expect(page.locator('[data-test="title"]')).to_have_text("Products")


def test_c03_lista_produtos_disponiveis_apos_login(page: Page) -> None:
    # Dado Estou na página de login da loja Swag Labs
    page.goto(BASE_URL + "/")
    # Quando Efetuo login com um utilizador válido e a respetiva password
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    # Então Na página de catálogo, é apresentada a lista de produtos disponíveis
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    # E A lista contém 6 produtos, cada um com nome, descrição e preço visíveis
    items = page.locator('[data-test="inventory-item"]')
    expect(items).to_have_count(6)
    for i in range(6):
        expect(items.nth(i).locator('[data-test="inventory-item-name"]')).to_be_visible()
        expect(items.nth(i).locator('[data-test="inventory-item-desc"]')).to_be_visible()
        expect(items.nth(i).locator('[data-test="inventory-item-price"]')).to_be_visible()
    # E Os produtos e preços apresentados são os seguintes: Sauce Labs Backpack $29.99; Sauce Labs Bike Light $9.99; Sauce Labs Bolt T-Shirt $15.99; Sauce Labs Fleece Jacket $49.99; Sauce Labs Onesie $7.99; Test.allTheThings() T-Shirt (Red) $15.99
    produtos = [
        ("Sauce Labs Backpack", "$29.99"),
        ("Sauce Labs Bike Light", "$9.99"),
        ("Sauce Labs Bolt T-Shirt", "$15.99"),
        ("Sauce Labs Fleece Jacket", "$49.99"),
        ("Sauce Labs Onesie", "$7.99"),
        ("Test.allTheThings() T-Shirt (Red)", "$15.99"),
    ]
    for i, (nome, preco) in enumerate(produtos):
        expect(items.nth(i).locator('[data-test="inventory-item-name"]')).to_have_text(nome)
        expect(items.nth(i).locator('[data-test="inventory-item-price"]')).to_have_text(preco)
