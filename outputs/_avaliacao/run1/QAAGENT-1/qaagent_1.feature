# language: pt
@QAAGENT-1
Funcionalidade: Autenticação de utilizador com credenciais válidas
  Validar que um cliente registado com credenciais válidas é autenticado, chega ao catálogo de produtos e vê o título e a lista de produtos disponíveis.

  @C01 @RN-LOGIN-01
  Cenário: C01 – Login com credenciais válidas redireciona para o catálogo
    Dado Estou na página de login da loja Swag Labs
    Quando Introduzo o utilizador válido standard_user
    E Introduzo a password secret_sauce
    E Submeto o formulário de login
    Então Sou redirecionado para a página de catálogo de produtos (/inventory.html)
    E O utilizador deixa de ver a página de login

  @C02 @RN-LOGIN-01
  Cenário: C02 – Título da secção de produtos visível após login
    Dado Estou na página de login da loja Swag Labs
    Quando Introduzo o utilizador válido standard_user
    E Introduzo a password secret_sauce
    E Submeto o formulário de login
    E Chego à página de catálogo de produtos
    Então O título da página de catálogo é visível com o texto "Products"

  @C03 @RN-LOGIN-01
  Cenário: C03 – Lista de produtos disponíveis apresentada após login
    Dado Estou na página de login da loja Swag Labs
    Quando Introduzo o utilizador válido standard_user
    E Introduzo a password secret_sauce
    E Submeto o formulário de login
    E Chego à página de catálogo de produtos
    Então É apresentada a lista de produtos com 6 produtos
    E Cada produto apresenta nome e preço
    E Os produtos apresentados são: Sauce Labs Backpack ($29.99), Sauce Labs Bike Light ($9.99), Sauce Labs Bolt T-Shirt ($15.99), Sauce Labs Fleece Jacket ($49.99), Sauce Labs Onesie ($7.99) e Test.allTheThings() T-Shirt (Red) ($15.99)
