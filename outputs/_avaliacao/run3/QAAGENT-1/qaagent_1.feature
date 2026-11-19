# language: pt
@QAAGENT-1
Funcionalidade: Autenticação de utilizador com credenciais válidas
  Validar que um cliente com credenciais válidas é redirecionado para o catálogo de produtos, onde o título e a lista de produtos são apresentados.

  @C01 @RN-LOGIN-01
  Cenário: C01 – Login com credenciais válidas redireciona para o catálogo
    Dado Estou na página de login da aplicação
    Quando Introduzo o utilizador válido standard_user
    E Introduzo a password secret_sauce correspondente
    E Submeto o formulário de login
    Então Sou redirecionado para a página de catálogo de produtos
    E O endereço da página é /inventory.html

  @C02 @RN-LOGIN-01
  Cenário: C02 – Título da secção de produtos visível após login
    Dado Tenho sessão iniciada com o utilizador standard_user e a password secret_sauce
    Quando Estou na página de catálogo de produtos
    Então O título da secção de produtos está visível
    E O título apresentado é "Products"

  @C03 @RN-LOGIN-01
  Cenário: C03 – Lista de produtos disponíveis apresentada no catálogo
    Dado Tenho sessão iniciada com o utilizador standard_user e a password secret_sauce
    Quando Estou na página de catálogo de produtos
    Então É apresentada a lista de produtos disponíveis
    E A lista contém 6 produtos
    E Cada produto apresenta nome, descrição e preço
    E Os produtos e preços apresentados são: Sauce Labs Backpack $29.99, Sauce Labs Bike Light $9.99, Sauce Labs Bolt T-Shirt $15.99, Sauce Labs Fleece Jacket $49.99, Sauce Labs Onesie $7.99, Test.allTheThings() T-Shirt (Red) $15.99
