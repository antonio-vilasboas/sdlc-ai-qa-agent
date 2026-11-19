# language: pt
@QAAGENT-1
Funcionalidade: Autenticação de utilizador com credenciais válidas
  Validar que um cliente registado consegue autenticar-se com credenciais válidas, é redirecionado para o catálogo de produtos, vê o título "Products" e a lista de produtos disponíveis.

  @C01 @RN-LOGIN-01
  Cenário: C01 – Login com credenciais válidas redireciona para o catálogo
    Dado Estou na página de login da loja Swag Labs
    Quando Introduzo o utilizador válido e a respetiva password
    E Submeto o formulário de login
    Então Sou redirecionado para a página de catálogo de produtos
    E O endereço da página de destino é /inventory.html

  @C02 @RN-LOGIN-01
  Cenário: C02 – Título da secção de produtos visível após login
    Dado Estou na página de login da loja Swag Labs
    Quando Efetuo login com um utilizador válido e a respetiva password
    Então Na página de catálogo, o título da secção de produtos está visível
    E O título apresentado é "Products"

  @C03 @RN-LOGIN-01
  Cenário: C03 – Lista de produtos disponíveis apresentada após login
    Dado Estou na página de login da loja Swag Labs
    Quando Efetuo login com um utilizador válido e a respetiva password
    Então Na página de catálogo, é apresentada a lista de produtos disponíveis
    E A lista contém 6 produtos, cada um com nome, descrição e preço visíveis
    E Os produtos e preços apresentados são os seguintes: Sauce Labs Backpack $29.99; Sauce Labs Bike Light $9.99; Sauce Labs Bolt T-Shirt $15.99; Sauce Labs Fleece Jacket $49.99; Sauce Labs Onesie $7.99; Test.allTheThings() T-Shirt (Red) $15.99
