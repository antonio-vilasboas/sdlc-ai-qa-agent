# language: pt
@QAAGENT-6
Funcionalidade: [E2E] Finalização de encomenda (checkout completo)
  Validar o checkout completo na loja Swag Labs, desde a adição de um produto ao carrinho até à confirmação da encomenda, incluindo o cálculo do resumo e a validação dos campos obrigatórios.

  @C01 @RN-CART-01 @RN-CART-03 @RN-CART-05
  Cenário: C01 – Iniciar checkout com produto no carrinho
    Dado Estou autenticado com um utilizador válido
    E Estou no catálogo de produtos sem artigos no carrinho
    Quando Adiciono o produto Sauce Labs Backpack ao carrinho
    E Abro o carrinho
    E Inicio o checkout
    Então O produto é apresentado no carrinho com quantidade 1
    E O contador do carrinho indica 1 produto
    E O botão de adicionar do produto é substituído pelo botão de remover
    E É apresentado o formulário de informação do cliente com o título "Checkout: Your Information"

  @C02 @RN-CHK-01 @RN-CHK-03
  Cenário: C02 – Avançar com informação do cliente completa até ao resumo
    Dado Estou no formulário de informação do cliente com o produto Sauce Labs Backpack no carrinho
    Quando Preencho o primeiro nome, o apelido e o código postal
    E Continuo
    Então É apresentado o resumo da encomenda com o título "Checkout: Overview"
    E O resumo apresenta o artigo Sauce Labs Backpack com preço $29.99
    E É apresentada a informação de pagamento "SauceCard #31337"
    E É apresentada a informação de envio "Free Pony Express Delivery!"

  @C03 @RN-CHK-03 @RN-CHK-04 @RN-CHK-05
  Cenário: C03 – Verificar subtotal, taxa e total no resumo
    Dado Estou no resumo da encomenda com o produto Sauce Labs Backpack, de preço $29.99
    Quando Observo os valores de subtotal, taxa e total
    Então O subtotal ("Item total") é $29.99
    E A taxa ("Tax") é $2.40
    E O total é $32.39
    E O total corresponde à soma do subtotal com a taxa

  @C04 @RN-CHK-06 @RN-CART-02
  Cenário: C04 – Finalizar encomenda e ver confirmação
    Dado Estou no resumo da encomenda com o produto Sauce Labs Backpack no carrinho
    Quando Finalizo a encomenda
    Então É apresentada a página de confirmação em /checkout-complete.html
    E É apresentado o cabeçalho "Thank you for your order!"
    E É apresentado o texto "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    E O carrinho fica vazio e o contador do carrinho deixa de ser apresentado

  @C05 @RN-CHK-01 @RN-CHK-02
  Cenário: C05 – Bloquear avanço sem código postal
    Dado Estou no formulário de informação do cliente
    E Tenho preenchidos o primeiro nome e o apelido
    E O código postal está vazio
    Quando Continuo
    Então É apresentada a mensagem "Error: Postal Code is required"
    E Não avanço para o resumo da encomenda
    E Continuo no formulário de informação do cliente

  @C06 @RN-CHK-01 @RN-CHK-02
  Cenário: C06 – Mostrar apenas a primeira mensagem de campo obrigatório em falta
    Dado Estou no formulário de informação do cliente
    E O primeiro nome, o apelido e o código postal estão vazios
    Quando Continuo
    Então É apresentada apenas a mensagem "Error: First Name is required"
    E Não avanço para o resumo da encomenda
