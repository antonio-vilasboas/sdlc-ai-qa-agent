import re
from playwright.sync_api import Page, expect

def test_saucedemo_login_and_add_cart(page: Page):
    # 1. Navegar para a aplicação alvo
    page.goto("https://www.saucedemo.com/")
    
    # 2. Validar o título da página
    expect(page).to_have_title(re.compile("Swag Labs"))
    
    # 3. Autenticação com utilizador padrão
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    
    # 4. Validar redirecionamento e listagem de produtos
    expect(page).to_have_url(re.compile(r".*/inventory\.html"))
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    
    # 5. Adicionar um produto e verificar o contador do carrinho
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
