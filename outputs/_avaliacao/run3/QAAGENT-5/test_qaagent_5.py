"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-5: Gestão de artigos no carrinho de compras

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-5`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_adicionar_primeiro_artigo(page: Page) -> None:
    # Dado Estou autenticado na loja como cliente standard_user
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E Estou na página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E O carrinho está vazio e o contador do carrinho não é apresentado
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
    # Quando Adiciono o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # Então O produto Sauce Labs Backpack passa a ser apresentado com a opção de remover, no lugar da opção de adicionar
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    expect(page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')).to_have_count(0)
    # E O contador do carrinho no cabeçalho passa a indicar 1
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")


def test_c02_adicionar_segundo_artigo(page: Page) -> None:
    # Dado Estou autenticado na loja como cliente standard_user
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E Estou na página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E Já adicionei o produto Sauce Labs Backpack ao carrinho e o contador indica 1
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
    # Quando Adiciono o produto Sauce Labs Bike Light ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    # Então O produto Sauce Labs Bike Light passa a ser apresentado com a opção de remover
    expect(page.locator('[data-test="remove-sauce-labs-bike-light"]')).to_be_visible()
    expect(page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]')).to_have_count(0)
    # E O contador do carrinho no cabeçalho passa a indicar 2
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("2")


def test_c03_abrir_carrinho_com_dois_artigos(page: Page) -> None:
    # Dado Estou autenticado na loja como cliente standard_user
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E Adicionei os produtos Sauce Labs Backpack e Sauce Labs Bike Light ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    # E O contador do carrinho indica 2
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("2")
    # Quando Abro o carrinho através do ícone do carrinho no cabeçalho
    page.locator('[data-test="shopping-cart-link"]').click()
    # Então É apresentada a página do carrinho com o título "Your Cart"
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Your Cart")
    # E São apresentados os dois produtos adicionados: Sauce Labs Backpack com preço $29.99 e Sauce Labs Bike Light com preço $9.99
    items = page.locator('[data-test="inventory-item"]')
    expect(items).to_have_count(2)
    backpack = items.filter(has_text="Sauce Labs Backpack")
    bike_light = items.filter(has_text="Sauce Labs Bike Light")
    expect(backpack.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    expect(backpack.locator('[data-test="inventory-item-price"]')).to_have_text("$29.99")
    expect(bike_light.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Bike Light")
    expect(bike_light.locator('[data-test="inventory-item-price"]')).to_have_text("$9.99")
    # E Cada produto apresentado tem quantidade 1
    expect(backpack.locator('[data-test="item-quantity"]')).to_have_text("1")
    expect(bike_light.locator('[data-test="item-quantity"]')).to_have_text("1")


def test_c04_remover_artigo_do_carrinho(page: Page) -> None:
    # Dado Estou autenticado na loja como cliente standard_user
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E Adicionei os produtos Sauce Labs Backpack e Sauce Labs Bike Light ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("2")
    # E Estou na página do carrinho com os dois produtos apresentados
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    items = page.locator('[data-test="inventory-item"]')
    expect(items).to_have_count(2)
    # Quando Removo o produto Sauce Labs Backpack no carrinho
    page.locator('[data-test="remove-sauce-labs-backpack"]').click()
    # Então O produto Sauce Labs Backpack deixa de ser apresentado na lista do carrinho
    expect(items.filter(has_text="Sauce Labs Backpack")).to_have_count(0)
    # E O produto Sauce Labs Bike Light continua a ser apresentado na lista do carrinho
    expect(items.filter(has_text="Sauce Labs Bike Light")).to_have_count(1)
    # E O contador do carrinho no cabeçalho passa a indicar 1
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
