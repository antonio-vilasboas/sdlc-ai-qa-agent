"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-4: Ordenação de produtos no catálogo

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-4`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_ordenar_preco_ascendente(page: Page) -> None:
    # Dado O cliente está autenticado e encontra-se na página de catálogo de produtos
    page.goto(BASE_URL + "/")
    page.locator('[data-test="user-name"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Quando O cliente seleciona a ordenação "Price (low to high)" no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option(label='Price (low to high)')
    # Então Os seis produtos são apresentados por ordem crescente de preço, do mais barato para o mais caro
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(6)
    # E Os preços apresentados, por ordem, são $7.99, $9.99, $15.99, $15.99, $29.99 e $49.99
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text(['$7.99', '$9.99', '$15.99', '$15.99', '$29.99', '$49.99'])
    # E A opção ativa do seletor de ordenação apresenta o texto "Price (low to high)"
    expect(page.locator('[data-test="active-option"]')).to_have_text('Price (low to high)')


def test_c02_ordenar_preco_descendente(page: Page) -> None:
    # Dado O cliente está autenticado e encontra-se na página de catálogo de produtos
    page.goto(BASE_URL + "/")
    page.locator('[data-test="user-name"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Quando O cliente seleciona a ordenação "Price (high to low)" no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option(label='Price (high to low)')
    # Então Os seis produtos são apresentados por ordem decrescente de preço, do mais caro para o mais barato
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(6)
    # E Os preços apresentados, por ordem, são $49.99, $29.99, $15.99, $15.99, $9.99 e $7.99
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text(['$49.99', '$29.99', '$15.99', '$15.99', '$9.99', '$7.99'])
    # E A opção ativa do seletor de ordenação apresenta o texto "Price (high to low)"
    expect(page.locator('[data-test="active-option"]')).to_have_text('Price (high to low)')


def test_c03_ordenar_nome_z_a(page: Page) -> None:
    # Dado O cliente está autenticado e encontra-se na página de catálogo de produtos
    page.goto(BASE_URL + "/")
    page.locator('[data-test="user-name"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Quando O cliente seleciona a ordenação "Name (Z to A)" no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option(label='Name (Z to A)')
    # Então Os seis produtos são apresentados por ordem alfabética inversa de nome
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(6)
    # E A ordem apresentada é: Test.allTheThings() T-Shirt (Red), Sauce Labs Onesie, Sauce Labs Fleece Jacket, Sauce Labs Bolt T-Shirt, Sauce Labs Bike Light e Sauce Labs Backpack
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text(['Test.allTheThings() T-Shirt (Red)', 'Sauce Labs Onesie', 'Sauce Labs Fleece Jacket', 'Sauce Labs Bolt T-Shirt', 'Sauce Labs Bike Light', 'Sauce Labs Backpack'])
    # E A opção ativa do seletor de ordenação apresenta o texto "Name (Z to A)"
    expect(page.locator('[data-test="active-option"]')).to_have_text('Name (Z to A)')
