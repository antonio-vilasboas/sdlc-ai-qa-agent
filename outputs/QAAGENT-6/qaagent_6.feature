# language: pt
@QAAGENT-6
Funcionalidade: [E2E] Finalização de encomenda (checkout completo)
  Validar o checkout completo, desde o formulário de informação do cliente até à confirmação da encomenda, incluindo o cálculo de subtotal, taxa e total e as validações obrigatórias dos campos.

  @C01 @RN-CART-01 @RN-CART-03 @RN-CART-05 @RN-CHK-01
  Cenário: C01 – Acesso ao formulário de informação do cliente a partir do carrinho
    Dado Estou autenticado com um utilizador válido
    E O carrinho não tem produtos
    Quando Adiciono o produto Sauce Labs Backpack ao carrinho
    E Abro o carrinho
    E Inicio o checkout
    Então É apresentado o formulário de informação do cliente com os campos primeiro nome, apelido e código postal
    E O título da página é "Checkout: Your Information"
    E O contador do carrinho apresenta 1 produto

  @C02 @RN-CHK-01
  Cenário: C02 – Avanço para o resumo com dados válidos do cliente
    Dado Estou autenticado com um utilizador válido
    E Adicionei o produto Sauce Labs Backpack ao carrinho
    E Estou no formulário de informação do cliente
    Quando Preencho o primeiro nome, o apelido e o código postal com dados válidos
    E Continuo
    Então É apresentado o resumo da encomenda
    E O título da página é "Checkout: Overview"
    E O resumo apresenta o produto Sauce Labs Backpack com preço $29.99

  @C03 @RN-CHK-03 @RN-CHK-04 @RN-CHK-05
  Cenário: C03 – Cálculo de subtotal, taxa e total no resumo
    Dado Estou autenticado com um utilizador válido
    E Adicionei o produto Sauce Labs Backpack ao carrinho
    E Preenchi os dados obrigatórios do cliente com valores válidos e continuei para o resumo
    Quando Observo os valores apresentados no resumo da encomenda
    Então O subtotal é "Item total: $29.99"
    E A taxa é "Tax: $2.40"
    E O total é "Total: $32.39"
    E O total é igual à soma do subtotal com a taxa

  @C04 @RN-CHK-06 @RN-CART-02
  Cenário: C04 – Confirmação da encomenda após finalizar
    Dado Estou autenticado com um utilizador válido
    E Adicionei o produto Sauce Labs Backpack ao carrinho
    E Estou no resumo da encomenda
    Quando Finalizo a encomenda
    Então É apresentada a confirmação da encomenda com o cabeçalho "Thank you for your order!"
    E É apresentado o texto "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    E O endereço da página é "/checkout-complete.html"
    E O contador do carrinho deixa de ser apresentado

  @C05 @RN-CHK-01 @RN-CHK-02
  Cenário: C05 – Erro ao continuar sem código postal
    Dado Estou autenticado com um utilizador válido
    E Adicionei o produto Sauce Labs Backpack ao carrinho
    E Estou no formulário de informação do cliente
    E Preenchi o primeiro nome e o apelido com valores válidos
    Quando Deixo o código postal vazio
    E Continuo
    Então É apresentada a mensagem "Error: Postal Code is required"
    E Continuo no formulário de informação do cliente
    E O resumo da encomenda não é apresentado

  @C06 @RN-CHK-01 @RN-CHK-02
  Cenário: C06 – Mensagem de erro do primeiro campo em falta quando todos estão vazios
    Dado Estou autenticado com um utilizador válido
    E Adicionei o produto Sauce Labs Backpack ao carrinho
    E Estou no formulário de informação do cliente
    Quando Deixo os três campos vazios
    E Continuo
    Então É apresentada apenas a mensagem "Error: First Name is required"
    E Continuo no formulário de informação do cliente
    E O resumo da encomenda não é apresentado

  @C07 @RN-CHK-01 @RN-CHK-02
  Cenário: C07 – Erro ao continuar sem apelido
    Dado Estou autenticado com um utilizador válido
    E Adicionei o produto Sauce Labs Backpack ao carrinho
    E Estou no formulário de informação do cliente
    E Preenchi o primeiro nome e o código postal com valores válidos
    Quando Deixo o apelido vazio
    E Continuo
    Então É apresentada a mensagem "Error: Last Name is required"
    E Continuo no formulário de informação do cliente
    E O resumo da encomenda não é apresentado
