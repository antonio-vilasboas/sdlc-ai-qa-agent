"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-5: Gestão de artigos no carrinho de compras

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-5`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_adicionar_primeiro_artigo(page: Page) -> None:
    # Dado o utilizador 'standard_user' está autenticado e na página de catálogo de produtos
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E o carrinho está vazio
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
    # Quando o utilizador adiciona o produto 'Sauce Labs Backpack' ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # Então o contador do carrinho passa a indicar 1
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
    # E o botão do produto 'Sauce Labs Backpack' passa a ser o botão de remover do carrinho
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    expect(page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')).to_have_count(0)


def test_c02_adicionar_segundo_artigo(page: Page) -> None:
    # Dado o utilizador 'standard_user' está autenticado na página de catálogo de produtos
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E o produto 'Sauce Labs Backpack' já foi adicionado ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
    # Quando o utilizador adiciona o produto 'Sauce Labs Bike Light' ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    # Então o contador do carrinho passa a indicar 2
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("2")


def test_c03_visualizar_dois_artigos_carrinho(page: Page) -> None:
    # Dado o utilizador 'standard_user' está autenticado na página de catálogo de produtos
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E os produtos 'Sauce Labs Backpack' e 'Sauce Labs Bike Light' foram adicionados ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("2")
    # Quando o utilizador abre o carrinho através do ícone do carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Your Cart")
    # Então são apresentados dois artigos na lista do carrinho
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(2)
    # E é apresentado o artigo 'Sauce Labs Backpack' com o preço $29.99
    expect(page.locator('[data-test="inventory-item-name"]').nth(0)).to_have_text("Sauce Labs Backpack")
    expect(page.locator('[data-test="inventory-item-price"]').nth(0)).to_have_text("$29.99")
    # E é apresentado o artigo 'Sauce Labs Bike Light' com o preço $9.99
    expect(page.locator('[data-test="inventory-item-name"]').nth(1)).to_have_text("Sauce Labs Bike Light")
    expect(page.locator('[data-test="inventory-item-price"]').nth(1)).to_have_text("$9.99")


def test_c04_remover_artigo_carrinho(page: Page) -> None:
    # Dado o utilizador 'standard_user' está autenticado
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E os produtos 'Sauce Labs Backpack' e 'Sauce Labs Bike Light' foram adicionados ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("2")
    # E o utilizador está na página do carrinho com os dois artigos apresentados
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(2)
    # Quando o utilizador remove o produto 'Sauce Labs Backpack' no carrinho
    page.locator('[data-test="remove-sauce-labs-backpack"]').click()
    # Então o produto 'Sauce Labs Backpack' deixa de ser apresentado na lista do carrinho
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_have_count(0)
    # E o produto 'Sauce Labs Bike Light' continua a ser apresentado
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(1)
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Bike Light")
    # E o contador do carrinho passa a indicar 1
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")


def test_c05_contador_oculto_carrinho_vazio(page: Page) -> None:
    # Dado o utilizador 'standard_user' está autenticado
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E apenas o produto 'Sauce Labs Backpack' foi adicionado ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
    # E o utilizador está na página do carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(1)
    # Quando o utilizador remove o produto 'Sauce Labs Backpack' no carrinho
    page.locator('[data-test="remove-sauce-labs-backpack"]').click()
    # Então o produto deixa de ser apresentado na lista do carrinho
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(0)
    # E o contador do carrinho deixa de ser apresentado
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
