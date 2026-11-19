# language: pt
@QAAGENT-5
Funcionalidade: Gestão de artigos no carrinho de compras
  Validar que o utilizador autenticado consegue adicionar e remover artigos do carrinho e que o contador e a lista do carrinho refletem essas ações.

  @C01 @RN-CART-01 @RN-CART-02 @RN-CART-03 @RN-CART-05
  Cenário: C01 – Adicionar primeiro artigo ao carrinho atualiza o contador para 1
    Dado Estou autenticado na loja como cliente standard_user
    E Estou na página de catálogo de produtos
    E O carrinho está vazio e o contador do carrinho não é apresentado
    Quando Adiciono o produto Sauce Labs Backpack ao carrinho
    Então O produto Sauce Labs Backpack passa a ser apresentado com a opção de remover, no lugar da opção de adicionar
    E O contador do carrinho no cabeçalho passa a indicar 1

  @C02 @RN-CART-01 @RN-CART-03 @RN-CART-05
  Cenário: C02 – Adicionar segundo artigo ao carrinho atualiza o contador para 2
    Dado Estou autenticado na loja como cliente standard_user
    E Estou na página de catálogo de produtos
    E Já adicionei o produto Sauce Labs Backpack ao carrinho e o contador indica 1
    Quando Adiciono o produto Sauce Labs Bike Light ao carrinho
    Então O produto Sauce Labs Bike Light passa a ser apresentado com a opção de remover
    E O contador do carrinho no cabeçalho passa a indicar 2

  @C03 @RN-CART-01 @RN-CART-05
  Cenário: C03 – Abrir o carrinho apresenta os dois artigos adicionados
    Dado Estou autenticado na loja como cliente standard_user
    E Adicionei os produtos Sauce Labs Backpack e Sauce Labs Bike Light ao carrinho
    E O contador do carrinho indica 2
    Quando Abro o carrinho através do ícone do carrinho no cabeçalho
    Então É apresentada a página do carrinho com o título "Your Cart"
    E São apresentados os dois produtos adicionados: Sauce Labs Backpack com preço $29.99 e Sauce Labs Bike Light com preço $9.99
    E Cada produto apresentado tem quantidade 1

  @C04 @RN-CART-01 @RN-CART-04
  Cenário: C04 – Remover um artigo no carrinho retira-o da lista e atualiza o contador para 1
    Dado Estou autenticado na loja como cliente standard_user
    E Adicionei os produtos Sauce Labs Backpack e Sauce Labs Bike Light ao carrinho
    E Estou na página do carrinho com os dois produtos apresentados
    Quando Removo o produto Sauce Labs Backpack no carrinho
    Então O produto Sauce Labs Backpack deixa de ser apresentado na lista do carrinho
    E O produto Sauce Labs Bike Light continua a ser apresentado na lista do carrinho
    E O contador do carrinho no cabeçalho passa a indicar 1
