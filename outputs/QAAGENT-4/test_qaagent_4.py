"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-4: Ordenação de produtos no catálogo

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-4`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_ordenar_preco_ascendente(page: Page) -> None:
    # Dado O cliente está autenticado na página de catálogo de produtos
    # (PENDENTE: credenciais e seletores de login não constam do contexto; ver assumptions)
    page.goto(BASE_URL + "/inventory.html")
    # Quando O cliente escolhe a ordenação "Price (low to high)" no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option(label='Price (low to high)')
    # Então Os produtos são apresentados do mais barato para o mais caro, pela sequência de preços $7.99, $9.99, $15.99, $15.99, $29.99, $49.99
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text(['$7.99', '$9.99', '$15.99', '$15.99', '$29.99', '$49.99'])
    # E A opção ativa do seletor apresenta o texto "Price (low to high)"
    expect(page.locator('[data-test="active-option"]')).to_have_text('Price (low to high)')
    # E A verificação incide na sequência de preços; a posição relativa entre os dois produtos de $15.99 não é validada
    # (a asserção acima valida apenas a sequência de preços, conforme RN-ORD-03)


def test_c02_ordenar_preco_descendente(page: Page) -> None:
    # Dado O cliente está autenticado na página de catálogo de produtos
    # (PENDENTE: credenciais e seletores de login não constam do contexto; ver assumptions)
    page.goto(BASE_URL + "/inventory.html")
    # Quando O cliente escolhe a ordenação "Price (high to low)" no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option(label='Price (high to low)')
    # Então Os produtos são apresentados do mais caro para o mais barato, pela sequência de preços $49.99, $29.99, $15.99, $15.99, $9.99, $7.99
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text(['$49.99', '$29.99', '$15.99', '$15.99', '$9.99', '$7.99'])
    # E A opção ativa do seletor apresenta o texto "Price (high to low)"
    expect(page.locator('[data-test="active-option"]')).to_have_text('Price (high to low)')
    # E A verificação incide na sequência de preços; a posição relativa entre os dois produtos de $15.99 não é validada
    # (a asserção acima valida apenas a sequência de preços, conforme RN-ORD-03)


def test_c03_ordenar_nome_z_a(page: Page) -> None:
    # Dado O cliente está autenticado na página de catálogo de produtos
    # (PENDENTE: credenciais e seletores de login não constam do contexto; ver assumptions)
    page.goto(BASE_URL + "/inventory.html")
    # Quando O cliente escolhe a ordenação "Name (Z to A)" no seletor de ordenação
    page.locator('[data-test="product-sort-container"]').select_option(label='Name (Z to A)')
    # Então Os produtos são apresentados por ordem alfabética inversa: Test.allTheThings() T-Shirt (Red), Sauce Labs Onesie, Sauce Labs Fleece Jacket, Sauce Labs Bolt T-Shirt, Sauce Labs Bike Light, Sauce Labs Backpack
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text(['Test.allTheThings() T-Shirt (Red)', 'Sauce Labs Onesie', 'Sauce Labs Fleece Jacket', 'Sauce Labs Bolt T-Shirt', 'Sauce Labs Bike Light', 'Sauce Labs Backpack'])
    # E A opção ativa do seletor apresenta o texto "Name (Z to A)"
    expect(page.locator('[data-test="active-option"]')).to_have_text('Name (Z to A)')
