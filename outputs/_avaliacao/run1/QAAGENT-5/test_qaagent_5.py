"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-5: Gestão de artigos no carrinho de compras

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-5`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_adicionar_um_produto(page: Page) -> None:
    # Dado O utilizador está autenticado na loja como cliente padrão
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + '/inventory.html')
    # E O utilizador está na página de catálogo de produtos
    expect(page.locator('[data-test="title"]')).to_have_text('Products')
    # E O carrinho está vazio
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
    # Quando O utilizador adiciona o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # Então O contador do carrinho no cabeçalho é apresentado com o valor 1
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('1')
    # E O botão de adicionar do produto é substituído por um botão de remover
    expect(page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')).to_have_count(0)
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()


def test_c02_adicionar_segundo_produto(page: Page) -> None:
    # Dado O utilizador está autenticado na loja como cliente padrão
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + '/inventory.html')
    # E O utilizador está na página de catálogo com o produto Sauce Labs Backpack já adicionado ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('1')
    # Quando O utilizador adiciona o produto Sauce Labs Bike Light ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    # Então O contador do carrinho no cabeçalho é apresentado com o valor 2
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('2')
    # E O botão de remover é apresentado para o produto Sauce Labs Bike Light
    expect(page.locator('[data-test="remove-sauce-labs-bike-light"]')).to_be_visible()


def test_c03_carrinho_apresenta_dois_produtos(page: Page) -> None:
    # Dado O utilizador está autenticado na loja como cliente padrão
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + '/inventory.html')
    # E O utilizador adicionou os produtos Sauce Labs Backpack e Sauce Labs Bike Light ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('2')
    # Quando O utilizador abre o carrinho através do ícone do carrinho no cabeçalho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + '/cart.html')
    # Então A página do carrinho apresenta o título "Your Cart"
    expect(page.locator('[data-test="title"]')).to_have_text('Your Cart')
    # E São apresentados exatamente dois artigos: Sauce Labs Backpack e Sauce Labs Bike Light
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(2)
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text(['Sauce Labs Backpack', 'Sauce Labs Bike Light'])
    # E Cada artigo apresenta o preço correspondente ($29.99 e $9.99) e quantidade 1
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text(['$29.99', '$9.99'])
    expect(page.locator('[data-test="item-quantity"]')).to_have_text(['1', '1'])
    # E O contador do carrinho no cabeçalho continua a indicar 2
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('2')


def test_c04_remover_produto_do_carrinho(page: Page) -> None:
    # Dado O utilizador está autenticado na loja como cliente padrão
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + '/inventory.html')
    # E O utilizador tem os produtos Sauce Labs Backpack e Sauce Labs Bike Light no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('2')
    # Quando O utilizador abre o carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + '/cart.html')
    # E O utilizador remove o produto Sauce Labs Bike Light do carrinho
    page.locator('[data-test="remove-sauce-labs-bike-light"]').click()
    # Então O produto Sauce Labs Bike Light deixa de ser apresentado na lista do carrinho
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(1)
    # E O produto Sauce Labs Backpack continua apresentado no carrinho
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text('Sauce Labs Backpack')
    # E O contador do carrinho no cabeçalho passa a indicar 1
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('1')


def test_c05_contador_oculto_carrinho_vazio(page: Page) -> None:
    # Dado O utilizador está autenticado na loja como cliente padrão
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + '/inventory.html')
    # E O utilizador tem apenas o produto Sauce Labs Backpack no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('1')
    # Quando O utilizador abre o carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + '/cart.html')
    # E O utilizador remove o produto Sauce Labs Backpack do carrinho
    page.locator('[data-test="remove-sauce-labs-backpack"]').click()
    # Então A lista do carrinho fica sem artigos
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(0)
    # E O contador do carrinho deixa de ser apresentado no cabeçalho
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
