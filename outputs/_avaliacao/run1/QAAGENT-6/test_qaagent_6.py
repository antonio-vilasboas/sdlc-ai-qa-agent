"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-6: [E2E] Finalização de encomenda (checkout completo)

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-6`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_abrir_formulario_checkout(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O catálogo de produtos está apresentado
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    # Quando Adiciona o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    # E Abre o carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    # E Inicia o checkout
    page.locator('[data-test="checkout"]').click()
    # Então O contador do carrinho apresenta 1 produto
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
    # E É apresentado o formulário de informação do cliente com os campos primeiro nome, apelido e código postal
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    expect(page.locator('[data-test="firstName"]')).to_be_visible()
    expect(page.locator('[data-test="lastName"]')).to_be_visible()
    expect(page.locator('[data-test="postalCode"]')).to_be_visible()
    # E A página do formulário tem o título 'Checkout: Your Information'
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")


def test_c02_avancar_para_resumo(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O carrinho contém o produto Sauce Labs Backpack
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    page.locator('[data-test="checkout"]').click()
    # E O utilizador está no formulário de informação do cliente
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    # Quando Preenche o primeiro nome, o apelido e o código postal
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-001")
    # E Continua
    page.locator('[data-test="continue"]').click()
    # Então É apresentado o resumo da encomenda com o título 'Checkout: Overview'
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Overview")
    # E O resumo apresenta o produto Sauce Labs Backpack com o preço $29.99
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text("$29.99")
    # E O resumo apresenta a informação de pagamento 'SauceCard #31337' e a informação de envio 'Free Pony Express Delivery!'
    expect(page.locator('[data-test="payment-info-value"]')).to_have_text("SauceCard #31337")
    expect(page.locator('[data-test="shipping-info-value"]')).to_have_text("Free Pony Express Delivery!")


def test_c03_valores_subtotal_taxa_total(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O carrinho contém o produto Sauce Labs Backpack
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    page.locator('[data-test="checkout"]').click()
    # E O utilizador está no resumo da encomenda após preencher os dados do cliente
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-001")
    page.locator('[data-test="continue"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    # Quando Observa os valores de subtotal, taxa e total do resumo
    subtotal = page.locator('[data-test="subtotal-label"]')
    taxa = page.locator('[data-test="tax-label"]')
    total = page.locator('[data-test="total-label"]')
    # Então O subtotal ('Item total') é $29.99
    expect(subtotal).to_have_text("Item total: $29.99")
    # E A taxa ('Tax') é $2.40, correspondente a 8% do subtotal arredondado a 2 casas decimais
    expect(taxa).to_have_text("Tax: $2.40")
    # E O total é $32.39, igual à soma do subtotal com a taxa
    expect(total).to_have_text("Total: $32.39")


def test_c04_confirmar_encomenda_carrinho_vazio(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O carrinho contém o produto Sauce Labs Backpack
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    page.locator('[data-test="checkout"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-001")
    page.locator('[data-test="continue"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    # E O utilizador está no resumo da encomenda
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Overview")
    # Quando Finaliza a encomenda
    page.locator('[data-test="finish"]').click()
    # Então É apresentada a confirmação da encomenda com o cabeçalho 'Thank you for your order!'
    expect(page).to_have_url(BASE_URL + "/checkout-complete.html")
    expect(page.locator('[data-test="complete-header"]')).to_have_text("Thank you for your order!")
    # E É apresentado o texto 'Your order has been dispatched, and will arrive just as fast as the pony can get there!'
    expect(page.locator('[data-test="complete-text"]')).to_have_text("Your order has been dispatched, and will arrive just as fast as the pony can get there!")
    # E O contador do carrinho deixa de ser apresentado
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
    # E A página de confirmação tem o título 'Checkout: Complete!'
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Complete!")


def test_c05_impedir_avanco_sem_codigo_postal(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O carrinho contém o produto Sauce Labs Backpack
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    page.locator('[data-test="checkout"]').click()
    # E O utilizador está no formulário de informação do cliente
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    # Quando Preenche o primeiro nome e o apelido
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    # E Deixa o código postal vazio
    expect(page.locator('[data-test="postalCode"]')).to_have_value("")
    # E Continua
    page.locator('[data-test="continue"]').click()
    # Então É apresentada a mensagem de erro 'Error: Postal Code is required'
    expect(page.locator('[data-test="error"]')).to_have_text("Error: Postal Code is required")
    # E A aplicação não avança para o resumo da encomenda
    expect(page).not_to_have_url(BASE_URL + "/checkout-step-two.html")
    # E O utilizador permanece no formulário de informação do cliente
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
