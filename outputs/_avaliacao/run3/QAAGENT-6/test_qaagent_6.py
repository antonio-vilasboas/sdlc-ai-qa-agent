"""Testes E2E gerados automaticamente pelo Agente Gerador — QAAGENT-6: [E2E] Finalização de encomenda (checkout completo)

Não editar à mão: regenerar com `python scripts/run_generator.py QAAGENT-6`.
"""

import re  # noqa: F401 — disponível para expect(...).to_have_url(re.compile(...))

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com"


def test_c01_abrir_formulario_informacao_cliente(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O carrinho está vazio
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)
    # Quando Adiciona o produto Sauce Labs Backpack ao carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # Então O botão do produto passa a ser o de remover do carrinho
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    # E O contador do carrinho indica 1 produto
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
    # E Abre o carrinho
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    # E Inicia o checkout
    page.locator('[data-test="checkout"]').click()
    # Então É apresentado o título da página de informação do cliente
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    # E O formulário apresenta os campos primeiro nome, apelido e código postal
    expect(page.locator('[data-test="firstName"]')).to_be_visible()
    expect(page.locator('[data-test="lastName"]')).to_be_visible()
    expect(page.locator('[data-test="postalCode"]')).to_be_visible()


def test_c02_avancar_resumo_encomenda(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O produto Sauce Labs Backpack está no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    # E O utilizador está no formulário de informação do cliente
    page.locator('[data-test="checkout"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    # Quando Preenche o primeiro nome, o apelido e o código postal
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    # E Continua
    page.locator('[data-test="continue"]').click()
    # Então É apresentado o título do resumo da encomenda
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Overview")
    # E O resumo apresenta o artigo Sauce Labs Backpack
    expect(page.locator('[data-test="inventory-item-name"]')).to_have_text("Sauce Labs Backpack")
    # E O resumo apresenta o preço $29.99 do artigo
    expect(page.locator('[data-test="inventory-item-price"]')).to_have_text("$29.99")
    # E O resumo apresenta a informação de pagamento SauceCard #31337
    expect(page.locator('[data-test="payment-info-value"]')).to_have_text("SauceCard #31337")
    # E O resumo apresenta a informação de envio Free Pony Express Delivery!
    expect(page.locator('[data-test="shipping-info-value"]')).to_have_text("Free Pony Express Delivery!")


def test_c03_verificar_subtotal_taxa_total(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O produto Sauce Labs Backpack está no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    page.locator('[data-test="checkout"]').click()
    # E O utilizador está no resumo da encomenda com o produto Sauce Labs Backpack
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    page.locator('[data-test="continue"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Overview")
    # Quando Lê os valores de subtotal, taxa e total apresentados
    subtotal = page.locator('[data-test="subtotal-label"]')
    taxa = page.locator('[data-test="tax-label"]')
    total = page.locator('[data-test="total-label"]')
    # Então O subtotal apresentado é $29.99
    expect(subtotal).to_have_text("Item total: $29.99")
    # E A taxa apresentada é $2.40
    expect(taxa).to_have_text("Tax: $2.40")
    # E O total apresentado é $32.39
    expect(total).to_have_text("Total: $32.39")
    # E O total é igual à soma do subtotal com a taxa
    # ($29.99 + $2.40 = $32.39; a igualdade é verificada pelos valores exatos acima)
    expect(total).to_contain_text("32.39")


def test_c04_finalizar_encomenda_confirmacao(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O produto Sauce Labs Backpack está no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    page.locator('[data-test="checkout"]').click()
    # E O utilizador está no resumo da encomenda
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    page.locator('[data-test="postalCode"]').fill("1000-100")
    page.locator('[data-test="continue"]').click()
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Overview")
    # Quando Finaliza a encomenda
    page.locator('[data-test="finish"]').click()
    expect(page).to_have_url(BASE_URL + "/checkout-complete.html")
    # Então É apresentado o cabeçalho de confirmação Thank you for your order!
    expect(page.locator('[data-test="complete-header"]')).to_have_text("Thank you for your order!")
    # E É apresentado o texto Your order has been dispatched, and will arrive just as fast as the pony can get there!
    expect(page.locator('[data-test="complete-text"]')).to_have_text("Your order has been dispatched, and will arrive just as fast as the pony can get there!")
    # E O contador do carrinho deixa de ser apresentado
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_count(0)


def test_c05_impedir_avanco_sem_codigo_postal(page: Page) -> None:
    # Dado O utilizador está autenticado com um utilizador válido
    page.goto(BASE_URL + "/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    expect(page).to_have_url(BASE_URL + "/inventory.html")
    # E O produto Sauce Labs Backpack está no carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).to_be_visible()
    page.locator('[data-test="shopping-cart-link"]').click()
    expect(page).to_have_url(BASE_URL + "/cart.html")
    page.locator('[data-test="checkout"]').click()
    # E O utilizador está no formulário de informação do cliente
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
    # Quando Preenche o primeiro nome e o apelido
    page.locator('[data-test="firstName"]').fill("Ana")
    page.locator('[data-test="lastName"]').fill("Silva")
    # E Deixa o código postal em branco
    # E Continua
    page.locator('[data-test="continue"]').click()
    # Então É apresentada a mensagem de erro Error: Postal Code is required
    expect(page.locator('[data-test="error"]')).to_have_text("Error: Postal Code is required")
    # E Não é apresentado o resumo da encomenda
    expect(page.locator('[data-test="finish"]')).to_have_count(0)
    # E O utilizador permanece no formulário de informação do cliente
    expect(page).to_have_url(BASE_URL + "/checkout-step-one.html")
    expect(page.locator('[data-test="title"]')).to_have_text("Checkout: Your Information")
