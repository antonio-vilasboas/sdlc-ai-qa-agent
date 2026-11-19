# language: pt
@QAAGENT-6
Funcionalidade: [E2E] Finalização de encomenda (checkout completo)
  Validar o fluxo ponta a ponta de compra, desde o carrinho com um produto até à confirmação da encomenda, incluindo os cálculos do resumo e a validação do código postal.

  @C01 @RN-CART-01 @RN-CART-03 @RN-CART-05 @RN-CHK-01
  Cenário: C01 – Abrir o formulário de informação do cliente a partir do carrinho
    Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    E O catálogo de produtos está apresentado
    Quando Adiciona o produto Sauce Labs Backpack ao carrinho
    E Abre o carrinho
    E Inicia o checkout
    Então O contador do carrinho apresenta 1 produto
    E É apresentado o formulário de informação do cliente com os campos primeiro nome, apelido e código postal
    E A página do formulário tem o título 'Checkout: Your Information'

  @C02 @RN-CHK-01 @RN-CHK-03
  Cenário: C02 – Avançar para o resumo com dados do cliente preenchidos
    Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    E O carrinho contém o produto Sauce Labs Backpack
    E O utilizador está no formulário de informação do cliente
    Quando Preenche o primeiro nome, o apelido e o código postal
    E Continua
    Então É apresentado o resumo da encomenda com o título 'Checkout: Overview'
    E O resumo apresenta o produto Sauce Labs Backpack com o preço $29.99
    E O resumo apresenta a informação de pagamento 'SauceCard #31337' e a informação de envio 'Free Pony Express Delivery!'

  @C03 @RN-CHK-03 @RN-CHK-04 @RN-CHK-05
  Cenário: C03 – Verificar subtotal, taxa e total no resumo da encomenda
    Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    E O carrinho contém o produto Sauce Labs Backpack
    E O utilizador está no resumo da encomenda após preencher os dados do cliente
    Quando Observa os valores de subtotal, taxa e total do resumo
    Então O subtotal ('Item total') é $29.99
    E A taxa ('Tax') é $2.40, correspondente a 8% do subtotal arredondado a 2 casas decimais
    E O total é $32.39, igual à soma do subtotal com a taxa

  @C04 @RN-CHK-06 @RN-CART-02
  Cenário: C04 – Confirmar a encomenda e verificar carrinho vazio
    Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    E O carrinho contém o produto Sauce Labs Backpack
    E O utilizador está no resumo da encomenda
    Quando Finaliza a encomenda
    Então É apresentada a confirmação da encomenda com o cabeçalho 'Thank you for your order!'
    E É apresentado o texto 'Your order has been dispatched, and will arrive just as fast as the pony can get there!'
    E O contador do carrinho deixa de ser apresentado
    E A página de confirmação tem o título 'Checkout: Complete!'

  @C05 @RN-CHK-01 @RN-CHK-02
  Cenário: C05 – Impedir avanço sem código postal
    Dado O utilizador está autenticado com um utilizador válido (ver US-01)
    E O carrinho contém o produto Sauce Labs Backpack
    E O utilizador está no formulário de informação do cliente
    Quando Preenche o primeiro nome e o apelido
    E Deixa o código postal vazio
    E Continua
    Então É apresentada a mensagem de erro 'Error: Postal Code is required'
    E A aplicação não avança para o resumo da encomenda
    E O utilizador permanece no formulário de informação do cliente
