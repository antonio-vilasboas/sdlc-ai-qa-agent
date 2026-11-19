# language: pt
@QAAGENT-5
Funcionalidade: Gestão de artigos no carrinho de compras
  Validar que o cliente autenticado consegue adicionar e remover artigos do carrinho, e que o contador e a lista do carrinho refletem essas alterações.

  @C01 @RN-CART-01 @RN-CART-03 @RN-CART-05
  Cenário: C01 – Adicionar um produto ao carrinho atualiza o contador para 1
    Dado O utilizador está autenticado na loja como cliente padrão
    E O utilizador está na página de catálogo de produtos
    E O carrinho está vazio
    Quando O utilizador adiciona o produto Sauce Labs Backpack ao carrinho
    Então O contador do carrinho no cabeçalho é apresentado com o valor 1
    E O botão de adicionar do produto é substituído por um botão de remover

  @C02 @RN-CART-01 @RN-CART-03 @RN-CART-05
  Cenário: C02 – Adicionar um segundo produto atualiza o contador para 2
    Dado O utilizador está autenticado na loja como cliente padrão
    E O utilizador está na página de catálogo com o produto Sauce Labs Backpack já adicionado ao carrinho
    Quando O utilizador adiciona o produto Sauce Labs Bike Light ao carrinho
    Então O contador do carrinho no cabeçalho é apresentado com o valor 2
    E O botão de remover é apresentado para o produto Sauce Labs Bike Light

  @C03 @RN-CART-01 @RN-CART-05
  Cenário: C03 – Carrinho apresenta os dois produtos adicionados
    Dado O utilizador está autenticado na loja como cliente padrão
    E O utilizador adicionou os produtos Sauce Labs Backpack e Sauce Labs Bike Light ao carrinho
    Quando O utilizador abre o carrinho através do ícone do carrinho no cabeçalho
    Então A página do carrinho apresenta o título "Your Cart"
    E São apresentados exatamente dois artigos: Sauce Labs Backpack e Sauce Labs Bike Light
    E Cada artigo apresenta o preço correspondente ($29.99 e $9.99) e quantidade 1
    E O contador do carrinho no cabeçalho continua a indicar 2

  @C04 @RN-CART-04 @RN-CART-01
  Cenário: C04 – Remover um produto no carrinho retira-o da lista e atualiza o contador para 1
    Dado O utilizador está autenticado na loja como cliente padrão
    E O utilizador tem os produtos Sauce Labs Backpack e Sauce Labs Bike Light no carrinho
    Quando O utilizador abre o carrinho
    E O utilizador remove o produto Sauce Labs Bike Light do carrinho
    Então O produto Sauce Labs Bike Light deixa de ser apresentado na lista do carrinho
    E O produto Sauce Labs Backpack continua apresentado no carrinho
    E O contador do carrinho no cabeçalho passa a indicar 1

  @C05 @RN-CART-02 @RN-CART-04
  Cenário: C05 – Contador deixa de ser apresentado quando o carrinho fica vazio
    Dado O utilizador está autenticado na loja como cliente padrão
    E O utilizador tem apenas o produto Sauce Labs Backpack no carrinho
    Quando O utilizador abre o carrinho
    E O utilizador remove o produto Sauce Labs Backpack do carrinho
    Então A lista do carrinho fica sem artigos
    E O contador do carrinho deixa de ser apresentado no cabeçalho
