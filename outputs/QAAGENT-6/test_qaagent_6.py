"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-6: [E2E] Finalização de encomenda (checkout completo)

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-6`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_acesso_formulario_checkout(page: Page) -> None:
    # Dado Estou autenticado com um utilizador válido
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text('Products')
    # E O carrinho não tem produtos
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
    # Quando Adiciono o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # E Abro o carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    # E Inicio o checkout
    page.locator('[data-test="checkout"]').click()
    # Então É apresentado o formulário de informação do cliente com os campos primeiro nome, apelido e código postal
    expect(page.locator('[data-test="firstName"]')).to_be_visible()
    expect(page.locator('[data-test="lastName"]')).to_be_visible()
    expect(page.locator('[data-test="postalCode"]')).to_be_visible()
    # E O título da página é "Checkout: Your Information"
    expect(page.locator('[data-test="title"]')).to_have_text('Checkout: Your Information')
    # E O contador do carrinho apresenta 1 produto
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text('1')


def test_c02_avanco_resumo_dados_validos(page: Page) -> None:
    # Dado Estou autenticado com um utilizador válido
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text('Products')
    # E Adicionei o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # E Estou no formulário de informação do cliente
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    # Quando Preencho o primeiro nome, o apelido e o código postal com dados válidos
    page.locator('[data-test="firstName"]').fill('Maria')
    page.locator('[data-test="lastName"]').fill('Silva')
    page.locator('[data-test="postalCode"]').fill('1000-001')
    # E Continuo
    page.locator('[data-test="continue"]').click()
    # Então É apresentado o resumo da encomenda
    expect(page.locator('[data-test="subtotal-label"]')).to_be_visible()
    # E O título da página é "Checkout: Overview"
    expect(page.locator('[data-test="title"]')).to_have_text('Checkout: Overview')
    # E O resumo apresenta o produto Sauce Labs Backpack com preço $29.99
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text('Sauce Labs Backpack')
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text('$29.99')


def test_c03_calculo_subtotal_taxa_total(page: Page) -> None:
    # Dado Estou autenticado com um utilizador válido
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text('Products')
    # E Adicionei o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # E Preenchi os dados obrigatórios do cliente com valores válidos e continuei para o resumo
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    page.locator('[data-test="firstName"]').fill('Maria')
    page.locator('[data-test="lastName"]').fill('Silva')
    page.locator('[data-test="postalCode"]').fill('1000-001')
    page.locator('[data-test="continue"]').click()
    # Quando Observo os valores apresentados no resumo da encomenda
    expect(page.locator('[data-test="subtotal-label"]')).to_be_visible()
    # Então O subtotal é "Item total: $29.99"
    expect(page.locator('[data-test="subtotal-label"]')).to_have_text('Item total: $29.99')
    # E A taxa é "Tax: $2.40"
    expect(page.locator('[data-test="tax-label"]')).to_have_text('Tax: $2.40')
    # E O total é "Total: $32.39"
    expect(page.locator('[data-test="total-label"]')).to_have_text('Total: $32.39')
    # E O total é igual à soma do subtotal com a taxa
    expect(page.locator('[data-test="total-label"]')).to_have_text('Total: $32.39')


def test_c04_confirmacao_encomenda(page: Page) -> None:
    # Dado Estou autenticado com um utilizador válido
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text('Products')
    # E Adicionei o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # E Estou no resumo da encomenda
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    page.locator('[data-test="firstName"]').fill('Maria')
    page.locator('[data-test="lastName"]').fill('Silva')
    page.locator('[data-test="postalCode"]').fill('1000-001')
    page.locator('[data-test="continue"]').click()
    expect(page.locator('[data-test="subtotal-label"]')).to_be_visible()
    # Quando Finalizo a encomenda
    page.locator('[data-test="finish"]').click()
    # Então É apresentada a confirmação da encomenda com o cabeçalho "Thank you for your order!"
    expect(page.locator('[data-test="complete-header"]')).to_have_text('Thank you for your order!')
    # E É apresentado o texto "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    expect(page.locator('[data-test="complete-text"]')).to_have_text('Your order has been dispatched, and will arrive just as fast as the pony can get there!')
    # E O endereço da página é "/checkout-complete.html"
    expect(page).to_have_url(BASE_URL + '/checkout-complete.html')
    # E O contador do carrinho deixa de ser apresentado
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)


def test_c05_erro_sem_codigo_postal(page: Page) -> None:
    # Dado Estou autenticado com um utilizador válido
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text('Products')
    # E Adicionei o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # E Estou no formulário de informação do cliente
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    # E Preenchi o primeiro nome e o apelido com valores válidos
    page.locator('[data-test="firstName"]').fill('Maria')
    page.locator('[data-test="lastName"]').fill('Silva')
    # Quando Deixo o código postal vazio
    # E Continuo
    page.locator('[data-test="continue"]').click()
    # Então É apresentada a mensagem "Error: Postal Code is required"
    expect(page.locator('[data-test="error"]')).to_have_text('Error: Postal Code is required')
    # E Continuo no formulário de informação do cliente
    expect(page.locator('[data-test="title"]')).to_have_text('Checkout: Your Information')
    # E O resumo da encomenda não é apresentado
    expect(page.locator('[data-test="finish"]')).to_have_count(0)


def test_c06_erro_primeiro_nome_em_falta(page: Page) -> None:
    # Dado Estou autenticado com um utilizador válido
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text('Products')
    # E Adicionei o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # E Estou no formulário de informação do cliente
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    # Quando Deixo os três campos vazios
    # E Continuo
    page.locator('[data-test="continue"]').click()
    # Então É apresentada apenas a mensagem "Error: First Name is required"
    expect(page.locator('[data-test="error"]')).to_have_count(1)
    expect(page.locator('[data-test="error"]')).to_have_text('Error: First Name is required')
    # E Continuo no formulário de informação do cliente
    expect(page.locator('[data-test="title"]')).to_have_text('Checkout: Your Information')
    # E O resumo da encomenda não é apresentado
    expect(page.locator('[data-test="finish"]')).to_have_count(0)


def test_c07_erro_sem_apelido(page: Page) -> None:
    # Dado Estou autenticado com um utilizador válido
    page.goto(BASE_URL + '/')
    page.locator('[data-test="username"]').fill('standard_user')
    page.locator('[data-test="password"]').fill('secret_sauce')
    page.locator('[data-test="login-button"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text('Products')
    # E Adicionei o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # E Estou no formulário de informação do cliente
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    # E Preenchi o primeiro nome e o código postal com valores válidos
    page.locator('[data-test="firstName"]').fill('Maria')
    page.locator('[data-test="postalCode"]').fill('1000-001')
    # Quando Deixo o apelido vazio
    # E Continuo
    page.locator('[data-test="continue"]').click()
    # Então É apresentada a mensagem "Error: Last Name is required"
    expect(page.locator('[data-test="error"]')).to_have_text('Error: Last Name is required')
    # E Continuo no formulário de informação do cliente
    expect(page.locator('[data-test="title"]')).to_have_text('Checkout: Your Information')
    # E O resumo da encomenda não é apresentado
    expect(page.locator('[data-test="finish"]')).to_have_count(0)
