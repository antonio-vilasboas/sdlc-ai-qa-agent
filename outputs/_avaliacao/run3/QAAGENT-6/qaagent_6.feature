# language: pt
@QAAGENT-6
Funcionalidade: [E2E] Finalização de encomenda (checkout completo)
  Validar o fluxo ponta a ponta de checkout, desde a adição de um produto ao carrinho até à confirmação da encomenda, incluindo o resumo com subtotal, taxa e total e a validação obrigatória do código postal.

  @C01 @RN-CART-01 @RN-CART-03 @RN-CART-05 @RN-CHK-01
  Cenário: C01 – Abrir o formulário de informação do cliente a partir do carrinho
    Dado O utilizador está autenticado com um utilizador válido
    E O carrinho está vazio
    Quando Adiciona o produto Sauce Labs Backpack ao carrinho
    E Abre o carrinho
    E Inicia o checkout
    Então É apresentado o título da página de informação do cliente
    E O botão do produto passa a ser o de remover do carrinho
    E O contador do carrinho indica 1 produto
    E O formulário apresenta os campos primeiro nome, apelido e código postal

  @C02 @RN-CHK-01 @RN-CHK-03
  Cenário: C02 – Avançar para o resumo da encomenda com o produto escolhido
    Dado O utilizador está autenticado com um utilizador válido
    E O produto Sauce Labs Backpack está no carrinho
    E O utilizador está no formulário de informação do cliente
    Quando Preenche o primeiro nome, o apelido e o código postal
    E Continua
    Então É apresentado o título do resumo da encomenda
    E O resumo apresenta o artigo Sauce Labs Backpack
    E O resumo apresenta o preço $29.99 do artigo
    E O resumo apresenta a informação de pagamento SauceCard #31337
    E O resumo apresenta a informação de envio Free Pony Express Delivery!

  @C03 @RN-CHK-03 @RN-CHK-04 @RN-CHK-05
  Cenário: C03 – Verificar subtotal, taxa e total no resumo da encomenda
    Dado O utilizador está autenticado com um utilizador válido
    E O produto Sauce Labs Backpack está no carrinho
    E O utilizador está no resumo da encomenda com o produto Sauce Labs Backpack
    Quando Lê os valores de subtotal, taxa e total apresentados
    Então O subtotal apresentado é $29.99
    E A taxa apresentada é $2.40
    E O total apresentado é $32.39
    E O total é igual à soma do subtotal com a taxa

  @C04 @RN-CHK-06 @RN-CART-02
  Cenário: C04 – Finalizar a encomenda e ver a confirmação
    Dado O utilizador está autenticado com um utilizador válido
    E O produto Sauce Labs Backpack está no carrinho
    E O utilizador está no resumo da encomenda
    Quando Finaliza a encomenda
    Então É apresentado o cabeçalho de confirmação Thank you for your order!
    E É apresentado o texto Your order has been dispatched, and will arrive just as fast as the pony can get there!
    E O contador do carrinho deixa de ser apresentado

  @C05 @RN-CHK-01 @RN-CHK-02
  Cenário: C05 – Impedir avanço sem código postal
    Dado O utilizador está autenticado com um utilizador válido
    E O produto Sauce Labs Backpack está no carrinho
    E O utilizador está no formulário de informação do cliente
    Quando Preenche o primeiro nome e o apelido
    E Deixa o código postal em branco
    E Continua
    Então É apresentada a mensagem de erro Error: Postal Code is required
    E Não é apresentado o resumo da encomenda
    E O utilizador permanece no formulário de informação do cliente
