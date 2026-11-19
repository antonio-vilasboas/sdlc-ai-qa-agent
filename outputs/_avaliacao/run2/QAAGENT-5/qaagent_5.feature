# language: pt
@QAAGENT-5
Funcionalidade: Gestão de artigos no carrinho de compras
  Validar que o utilizador autenticado consegue adicionar e remover artigos do carrinho, e que o contador do carrinho e a lista de artigos refletem essas ações.

  @C01 @RN-CART-01 @RN-CART-03 @RN-CART-05
  Cenário: C01 – Adicionar primeiro artigo ao carrinho
    Dado o utilizador 'standard_user' está autenticado e na página de catálogo de produtos
    E o carrinho está vazio
    Quando o utilizador adiciona o produto 'Sauce Labs Backpack' ao carrinho
    Então o contador do carrinho passa a indicar 1
    E o botão do produto 'Sauce Labs Backpack' passa a ser o botão de remover do carrinho

  @C02 @RN-CART-01 @RN-CART-05
  Cenário: C02 – Adicionar segundo artigo ao carrinho
    Dado o utilizador 'standard_user' está autenticado na página de catálogo de produtos
    E o produto 'Sauce Labs Backpack' já foi adicionado ao carrinho
    Quando o utilizador adiciona o produto 'Sauce Labs Bike Light' ao carrinho
    Então o contador do carrinho passa a indicar 2

  @C03 @RN-CART-01 @RN-CART-05
  Cenário: C03 – Visualizar os dois artigos no carrinho
    Dado o utilizador 'standard_user' está autenticado na página de catálogo de produtos
    E os produtos 'Sauce Labs Backpack' e 'Sauce Labs Bike Light' foram adicionados ao carrinho
    Quando o utilizador abre o carrinho através do ícone do carrinho
    Então são apresentados dois artigos na lista do carrinho
    E é apresentado o artigo 'Sauce Labs Backpack' com o preço $29.99
    E é apresentado o artigo 'Sauce Labs Bike Light' com o preço $9.99

  @C04 @RN-CART-04 @RN-CART-01
  Cenário: C04 – Remover um artigo no carrinho
    Dado o utilizador 'standard_user' está autenticado
    E os produtos 'Sauce Labs Backpack' e 'Sauce Labs Bike Light' foram adicionados ao carrinho
    E o utilizador está na página do carrinho com os dois artigos apresentados
    Quando o utilizador remove o produto 'Sauce Labs Backpack' no carrinho
    Então o produto 'Sauce Labs Backpack' deixa de ser apresentado na lista do carrinho
    E o produto 'Sauce Labs Bike Light' continua a ser apresentado
    E o contador do carrinho passa a indicar 1

  @C05 @RN-CART-02 @RN-CART-04
  Cenário: C05 – Contador oculto quando o carrinho fica vazio
    Dado o utilizador 'standard_user' está autenticado
    E apenas o produto 'Sauce Labs Backpack' foi adicionado ao carrinho
    E o utilizador está na página do carrinho
    Quando o utilizador remove o produto 'Sauce Labs Backpack' no carrinho
    Então o produto deixa de ser apresentado na lista do carrinho
    E o contador do carrinho deixa de ser apresentado
