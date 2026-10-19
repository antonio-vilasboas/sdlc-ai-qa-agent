# language: pt
@QAAGENT-4
Funcionalidade: Ordenação de produtos no catálogo
  Validar que o catálogo ordena corretamente os produtos por preço (ascendente e descendente) e por nome descendente (Z a A), com a opção ativa apresentada ao utilizador.

  @C01 @RN-ORD-02 @RN-ORD-03
  Cenário: C01 – Ordenar produtos por preço ascendente
    Dado O cliente está autenticado na página de catálogo de produtos
    Quando O cliente escolhe a ordenação "Price (low to high)" no seletor de ordenação
    Então Os produtos são apresentados do mais barato para o mais caro, pela sequência de preços $7.99, $9.99, $15.99, $15.99, $29.99, $49.99
    E A opção ativa do seletor apresenta o texto "Price (low to high)"
    E A verificação incide na sequência de preços; a posição relativa entre os dois produtos de $15.99 não é validada

  @C02 @RN-ORD-02 @RN-ORD-03
  Cenário: C02 – Ordenar produtos por preço descendente
    Dado O cliente está autenticado na página de catálogo de produtos
    Quando O cliente escolhe a ordenação "Price (high to low)" no seletor de ordenação
    Então Os produtos são apresentados do mais caro para o mais barato, pela sequência de preços $49.99, $29.99, $15.99, $15.99, $9.99, $7.99
    E A opção ativa do seletor apresenta o texto "Price (high to low)"
    E A verificação incide na sequência de preços; a posição relativa entre os dois produtos de $15.99 não é validada

  @C03 @RN-ORD-02
  Cenário: C03 – Ordenar produtos por nome descendente (Z a A)
    Dado O cliente está autenticado na página de catálogo de produtos
    Quando O cliente escolhe a ordenação "Name (Z to A)" no seletor de ordenação
    Então Os produtos são apresentados por ordem alfabética inversa: Test.allTheThings() T-Shirt (Red), Sauce Labs Onesie, Sauce Labs Fleece Jacket, Sauce Labs Bolt T-Shirt, Sauce Labs Bike Light, Sauce Labs Backpack
    E A opção ativa do seletor apresenta o texto "Name (Z to A)"
