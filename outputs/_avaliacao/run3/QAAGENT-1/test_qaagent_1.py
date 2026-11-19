"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-1: Autenticação de utilizador com credenciais válidas

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-1`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_login_valido(page: Page) -> None:
    # Dado Estou na página de login da aplicação
    page.goto(BASE_URL + "/")
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
    # Quando Introduzo o utilizador válido standard_user
    page.locator('[data-test="username"]').fill("standard_user")
    # E Introduzo a password secret_sauce correspondente
    page.locator('[data-test="password"]').fill("secret_sauce")
    # E Submeto o formulário de login
    page.locator('[data-test="login-button"]').click()
    # Então Sou redirecionado para a página de catálogo de produtos
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E O endereço da página é /inventory.html
    expect(page).to_have_url(BASE_URL + "/inventory.html")


def test_c02_titulo_produtos_visivel(page: Page) -> None:
    # Dado Tenho sessão iniciada com o utilizador standard_user e a password secret_sauce
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    # Quando Estou na página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Então O título da secção de produtos está visível
    titulo = page.locator('[data-test="title"]')
    expect(titulo).to_be_visible()
    # E O título apresentado é "Products"
    expect(titulo).to_have_text("Products")


def test_c03_lista_produtos_apresentada(page: Page) -> None:
    # Dado Tenho sessão iniciada com o utilizador standard_user e a password secret_sauce
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    # Quando Estou na página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Então É apresentada a lista de produtos disponíveis
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    # E A lista contém 6 produtos
    itens = page.locator('[data-test="inventory-item"]')
    expect(itens).to_have_count(6)
    # E Cada produto apresenta nome, descrição e preço
    for i in range(6):
        item = itens.nth(i)
        expect(item.locator('[data-test="inventory-item-name"]')).to_be_visible()
        expect(item.locator('[data-test="inventory-item-desc"]')).to_be_visible()
        expect(item.locator('[data-test="inventory-item-price"]')).to_be_visible()
    # E Os produtos e preços apresentados são: Sauce Labs Backpack $29.99, Sauce Labs Bike Light $9.99, Sauce Labs Bolt T-Shirt $15.99, Sauce Labs Fleece Jacket $49.99, Sauce Labs Onesie $7.99, Test.allTheThings() T-Shirt (Red) $15.99
    produtos_esperados = [
        ("Sauce Labs Backpack", "$29.99"),
        ("Sauce Labs Bike Light", "$9.99"),
        ("Sauce Labs Bolt T-Shirt", "$15.99"),
        ("Sauce Labs Fleece Jacket", "$49.99"),
        ("Sauce Labs Onesie", "$7.99"),
        ("Test.allTheThings() T-Shirt (Red)", "$15.99"),
    ]
    for i, (nome, preco) in enumerate(produtos_esperados):
        item = itens.nth(i)
        expect(item.locator('[data-test="inventory-item-name"]')).to_have_text(nome)
        expect(item.locator('[data-test="inventory-item-price"]')).to_have_text(preco)
