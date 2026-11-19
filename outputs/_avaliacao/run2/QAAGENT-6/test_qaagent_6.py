"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-6: [E2E] Finalização de encomenda (checkout completo)

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-6`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_iniciar_checkout(page: Page) -> None:
    page.goto(BASE_URL + "/")
    # Dado O cliente está autenticado com um utilizador válido
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    # E O catálogo de produtos está apresentado
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    # Quando Adiciona o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # Então O botão do produto passa a ser o de remover do carrinho
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    # E O contador do carrinho indica 1 artigo
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
    # E Abre o carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    # Então O carrinho apresenta o produto com quantidade 1
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text("$29.99")
    expect(page.locator('[data-test="item-quantity"]')).to_have_text("1")
    # E Inicia o checkout
    page.locator('[data-test="checkout"]').click()
    # E É apresentado o formulário de informação do cliente com o título "Checkout: Your Information"
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")


def test_c02_formulario_para_resumo(page: Page) -> None:
    page.goto(BASE_URL + "/")
    # Dado O cliente está autenticado com um utilizador válido
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Dado O produto Sauce Labs Backpack está no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    # Dado O cliente está no formulário de informação do cliente
    page.locator('[data-test="checkout"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    # Quando Preenche o primeiro nome, o apelido e o código postal
    page.locator('[data-test="firstName"]').fill("Teste")
    page.locator('[data-test="lastName"]').fill("Utilizador")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    # E Continua
    page.locator('[data-test="continue"]').click()
    # Então É apresentado o resumo da encomenda com o título "Checkout: Overview"
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Overview")
    # E O resumo apresenta o produto Sauce Labs Backpack com o preço $29.99
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text("$29.99")
    # E O resumo apresenta a informação de pagamento "SauceCard #31337" e a informação de envio "Free Pony Express Delivery!"
    expect(page.locator('[data-test="payment-info-value"]')).to_have_text("SauceCard #31337")
    expect(page.locator('[data-test="shipping-info-value"]')).to_have_text("Free Pony Express Delivery!")


def test_c03_subtotal_taxa_total(page: Page) -> None:
    page.goto(BASE_URL + "/")
    # Dado O cliente está autenticado com um utilizador válido
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Dado O produto Sauce Labs Backpack está no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    page.locator('[data-test="checkout"]').click()
    # Dado O cliente preencheu o formulário de informação do cliente e avançou para o resumo
    page.locator('[data-test="firstName"]').fill("Teste")
    page.locator('[data-test="lastName"]').fill("Utilizador")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    page.locator('[data-test="continue"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    # Quando Observa os valores apresentados no resumo da encomenda
    # Então O subtotal ("Item total") é $29.99
    expect(page.locator('[data-test="subtotal-label"]')).to_have_text("Item total: $29.99")
    # E A taxa ("Tax") é $2.40
    expect(page.locator('[data-test="tax-label"]')).to_have_text("Tax: $2.40")
    # E O total ("Total") é $32.39
    # E O total é igual à soma do subtotal com a taxa
    expect(page.locator('[data-test="total-label"]')).to_have_text("Total: $32.39")


def test_c04_finalizar_confirmacao(page: Page) -> None:
    page.goto(BASE_URL + "/")
    # Dado O cliente está autenticado com um utilizador válido
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Dado O produto Sauce Labs Backpack está no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    page.locator('[data-test="checkout"]').click()
    # Dado O cliente está no resumo da encomenda
    page.locator('[data-test="firstName"]').fill("Teste")
    page.locator('[data-test="lastName"]').fill("Utilizador")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    page.locator('[data-test="continue"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    # Quando Finaliza a encomenda
    page.locator('[data-test="finish"]').click()
    # Então É apresentada a página de confirmação, com URL "/checkout-complete.html"
    expect(page).to_have_url(BASE_URL + "/checkout-complete.html")
    # E O cabeçalho de confirmação é "Thank you for your order!"
    expect(page.locator('[data-test="complete-header"]')).to_have_text("Thank you for your order!")
    # E O texto de confirmação é "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    expect(page.locator('[data-test="complete-text"]')).to_have_text("Your order has been dispatched, and will arrive just as fast as the pony can get there!")
    # E O carrinho fica vazio e o contador do carrinho deixa de ser apresentado
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)


def test_c05_bloqueia_sem_codigo_postal(page: Page) -> None:
    page.goto(BASE_URL + "/")
    # Dado O cliente está autenticado com um utilizador válido
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # Dado O produto Sauce Labs Backpack está no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    page.locator('[data-test="checkout"]').click()
    # Dado O cliente está no formulário de informação do cliente
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    # Quando Preenche o primeiro nome e o apelido
    page.locator('[data-test="firstName"]').fill("Teste")
    page.locator('[data-test="lastName"]').fill("Utilizador")
    # E Deixa o código postal vazio
    # E Continua
    page.locator('[data-test="continue"]').click()
    # Então É apresentada a mensagem de erro "Error: Postal Code is required"
    expect(page.locator('[data-test="error"]')).to_have_text("Error: Postal Code is required")
    # E O cliente permanece no formulário de informação do cliente
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    # E O resumo da encomenda não é apresentado
    expect(page.locator('[data-test="payment-info-value"]')).to_have_count(0)
    expect(page.locator('[data-test="subtotal-label"]')).to_have_count(0)
