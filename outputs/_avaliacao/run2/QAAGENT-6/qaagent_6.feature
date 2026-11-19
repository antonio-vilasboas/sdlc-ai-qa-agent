# language: pt
@QAAGENT-6
Funcionalidade: [E2E] Finalização de encomenda (checkout completo)
  Validar o checkout completo, desde a seleção de um produto no carrinho até à confirmação da encomenda, incluindo as validações do formulário de informação do cliente e o cálculo do resumo.

  @C01 @RN-CART-01 @RN-CART-03 @RN-CART-05
  Cenário: C01 – Iniciar checkout com produto no carrinho
    Dado O cliente está autenticado com um utilizador válido
    E O catálogo de produtos está apresentado
    Quando Adiciona o produto Sauce Labs Backpack ao carrinho
    E Abre o carrinho
    E Inicia o checkout
    Então O botão do produto passa a ser o de remover do carrinho
    E O contador do carrinho indica 1 artigo
    E O carrinho apresenta o produto com quantidade 1
    E É apresentado o formulário de informação do cliente com o título "Checkout: Your Information"

  @C02 @RN-CHK-01 @RN-CHK-03
  Cenário: C02 – Avançar do formulário para o resumo com o produto escolhido
    Dado O cliente está autenticado com um utilizador válido
    E O produto Sauce Labs Backpack está no carrinho
    E O cliente está no formulário de informação do cliente
    Quando Preenche o primeiro nome, o apelido e o código postal
    E Continua
    Então É apresentado o resumo da encomenda com o título "Checkout: Overview"
    E O resumo apresenta o produto Sauce Labs Backpack com o preço $29.99
    E O resumo apresenta a informação de pagamento "SauceCard #31337" e a informação de envio "Free Pony Express Delivery!"

  @C03 @RN-CHK-03 @RN-CHK-04 @RN-CHK-05
  Cenário: C03 – Verificar subtotal, taxa e total no resumo
    Dado O cliente está autenticado com um utilizador válido
    E O produto Sauce Labs Backpack está no carrinho
    E O cliente preencheu o formulário de informação do cliente e avançou para o resumo
    Quando Observa os valores apresentados no resumo da encomenda
    Então O subtotal ("Item total") é $29.99
    E A taxa ("Tax") é $2.40
    E O total ("Total") é $32.39
    E O total é igual à soma do subtotal com a taxa

  @C04 @RN-CHK-06 @RN-CART-02
  Cenário: C04 – Finalizar encomenda e ver confirmação
    Dado O cliente está autenticado com um utilizador válido
    E O produto Sauce Labs Backpack está no carrinho
    E O cliente está no resumo da encomenda
    Quando Finaliza a encomenda
    Então É apresentada a página de confirmação, com URL "/checkout-complete.html"
    E O cabeçalho de confirmação é "Thank you for your order!"
    E O texto de confirmação é "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    E O carrinho fica vazio e o contador do carrinho deixa de ser apresentado

  @C05 @RN-CHK-01 @RN-CHK-02
  Cenário: C05 – Bloquear avanço sem código postal
    Dado O cliente está autenticado com um utilizador válido
    E O produto Sauce Labs Backpack está no carrinho
    E O cliente está no formulário de informação do cliente
    Quando Preenche o primeiro nome e o apelido
    E Deixa o código postal vazio
    E Continua
    Então É apresentada a mensagem de erro "Error: Postal Code is required"
    E O cliente permanece no formulário de informação do cliente
    E O resumo da encomenda não é apresentado
