"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-6: [E2E] Finalização de encomenda (checkout completo)

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-6`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_iniciar_checkout_com_produto_no_carrinho(page: Page) -> None:
    # Dado Estou autenticado com um utilizador válido
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    # E Estou no catálogo de produtos sem artigos no carrinho
    expect(page.locator('[data-test="inventory-list"]')).to_be_visible()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
    # Quando Adiciono o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    expect(page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')).to_have_count(0)
    # E Abro o carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    # Então O produto é apresentado no carrinho com quantidade 1
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    expect(page.locator('[data-test="item-quantity"]')).to_have_text("1")
    # E O contador do carrinho indica 1 produto
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
    # E O botão de adicionar do produto é substituído pelo botão de remover
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    # E Inicio o checkout
    page.locator('[data-test="checkout"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    # E É apresentado o formulário de informação do cliente com o título "Checkout: Your Information"
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    expect(page.locator('[data-test="firstName"]')).to_be_visible()


def test_c02_avancar_com_informacao_completa_ate_resumo(page: Page) -> None:
    # Dado Estou no formulário de informação do cliente com o produto Sauce Labs Backpack no carrinho
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    # Quando Preencho o primeiro nome, o apelido e o código postal
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    # E Continuo
    page.locator('[data-test="continue"]').click()
    # Então É apresentado o resumo da encomenda com o título "Checkout: Overview"
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Overview")
    # E O resumo apresenta o artigo Sauce Labs Backpack com preço $29.99
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text("$29.99")
    # E É apresentada a informação de pagamento "SauceCard #31337"
    expect(page.locator('[data-test="payment-info-value"]')).to_have_text("SauceCard #31337")
    # E É apresentada a informação de envio "Free Pony Express Delivery!"
    expect(page.locator('[data-test="shipping-info-value"]')).to_have_text("Free Pony Express Delivery!")


def test_c03_verificar_subtotal_taxa_e_total_no_resumo(page: Page) -> None:
    # Dado Estou no resumo da encomenda com o produto Sauce Labs Backpack, de preço $29.99
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    page.locator('[data-test="continue"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text("$29.99")
    # Quando Observo os valores de subtotal, taxa e total
    # Então O subtotal ("Item total") é $29.99
    expect(page.locator('[data-test="subtotal-label"]')).to_have_text("Item total: $29.99")
    # E A taxa ("Tax") é $2.40
    expect(page.locator('[data-test="tax-label"]')).to_have_text("Tax: $2.40")
    # E O total é $32.39
    expect(page.locator('[data-test="total-label"]')).to_have_text("Total: $32.39")
    # E O total corresponde à soma do subtotal com a taxa
    expect(page.locator('[data-test="total-label"]')).to_contain_text("$32.39")


def test_c04_finalizar_encomenda_e_ver_confirmacao(page: Page) -> None:
    # Dado Estou no resumo da encomenda com o produto Sauce Labs Backpack no carrinho
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    page.locator('[data-test="continue"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-step-two.html")
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    # Quando Finalizo a encomenda
    page.locator('[data-test="finish"]').click()
    # Então É apresentada a página de confirmação em /checkout-complete.html
    expect(page).to_have_url(BASE_URL + "/checkout-complete.html")
    # E É apresentado o cabeçalho "Thank you for your order!"
    expect(page.locator('[data-test="complete-header"]')).to_have_text("Thank you for your order!")
    # E É apresentado o texto "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    expect(page.locator('[data-test="complete-text"]')).to_have_text("Your order has been dispatched, and will arrive just as fast as the pony can get there!")
    # E O carrinho fica vazio e o contador do carrinho deixa de ser apresentado
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)


def test_c05_bloquear_avanco_sem_codigo_postal(page: Page) -> None:
    # Dado Estou no formulário de informação do cliente
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    # E Tenho preenchidos o primeiro nome e o apelido
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    # E O código postal está vazio
    expect(page.locator('[data-test="postalCode"]')).to_have_value("")
    # Quando Continuo
    page.locator('[data-test="continue"]').click()
    # Então É apresentada a mensagem "Error: Postal Code is required"
    expect(page.locator('[data-test="error"]')).to_have_text("Error: Postal Code is required")
    # E Não avanço para o resumo da encomenda
    expect(page).not_to_have_url(BASE_URL + "/checkout-step-two.html")
    # E Continuo no formulário de informação do cliente
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")


def test_c06_mostrar_apenas_primeira_mensagem_campo_em_falta(page: Page) -> None:
    # Dado Estou no formulário de informação do cliente
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    page.locator('[data-test="shopping-cart-link"]').click()
    page.locator('[data-test="checkout"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    # E O primeiro nome, o apelido e o código postal estão vazios
    expect(page.locator('[data-test="firstName"]')).to_have_value("")
    expect(page.locator('[data-test="lastName"]')).to_have_value("")
    expect(page.locator('[data-test="postalCode"]')).to_have_value("")
    # Quando Continuo
    page.locator('[data-test="continue"]').click()
    # Então É apresentada apenas a mensagem "Error: First Name is required"
    expect(page.locator('[data-test="error"]')).to_have_count(1)
    expect(page.locator('[data-test="error"]')).to_have_text("Error: First Name is required")
    # E Não avanço para o resumo da encomenda
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
