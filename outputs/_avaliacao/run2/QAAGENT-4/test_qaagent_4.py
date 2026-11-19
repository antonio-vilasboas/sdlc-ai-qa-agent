"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-4: Ordenação de produtos no catálogo

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-4`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_ordenar_preco_ascendente(page: Page) -> None:
    # Dado Estou autenticado na loja Swag Labs
    page.goto(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E Estou na página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    # Quando Escolho a ordenação por preço ascendente no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option("lohi")
    # Então Os seis produtos são apresentados do mais barato para o mais caro
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(6)
    # E A sequência de preços apresentada é $7.99, $9.99, $15.99, $15.99, $29.99, $49.99
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text(["$7.99", "$9.99", "$15.99", "$15.99", "$29.99", "$49.99"])
    # E A opção ativa do seletor apresenta 'Price (low to high)'
    expect(page.locator('[data-test="active-option"]')).to_have_text("Price (low to high)")


def test_c02_ordenar_preco_descendente(page: Page) -> None:
    # Dado Estou autenticado na loja Swag Labs
    page.goto(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E Estou na página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    # Quando Escolho a ordenação por preço descendente no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option("hilo")
    # Então Os seis produtos são apresentados do mais caro para o mais barato
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(6)
    # E A sequência de preços apresentada é $49.99, $29.99, $15.99, $15.99, $9.99, $7.99
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text(["$49.99", "$29.99", "$15.99", "$15.99", "$9.99", "$7.99"])
    # E A opção ativa do seletor apresenta 'Price (high to low)'
    expect(page.locator('[data-test="active-option"]')).to_have_text("Price (high to low)")


def test_c03_ordenar_nome_descendente(page: Page) -> None:
    # Dado Estou autenticado na loja Swag Labs
    page.goto(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E Estou na página de catálogo de produtos
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    # Quando Escolho a ordenação por nome descendente (Z a A) no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option("za")
    # Então Os seis produtos são apresentados por ordem alfabética inversa dos nomes
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(6)
    # E A sequência de nomes apresentada é Test.allTheThings() T-Shirt (Red), Sauce Labs Onesie, Sauce Labs Fleece Jacket, Sauce Labs Bolt T-Shirt, Sauce Labs Bike Light, Sauce Labs Backpack
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text(["Test.allTheThings() T-Shirt (Red)", "Sauce Labs Onesie", "Sauce Labs Fleece Jacket", "Sauce Labs Bolt T-Shirt", "Sauce Labs Bike Light", "Sauce Labs Backpack"])
    # E A opção ativa do seletor apresenta 'Name (Z to A)'
    expect(page.locator('[data-test="active-option"]')).to_have_text("Name (Z to A)")
