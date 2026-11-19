# language: pt
@QAAGENT-4
Funcionalidade: Ordenação de produtos no catálogo
  Validar que o seletor de ordenação do catálogo reordena corretamente os seis produtos por preço ascendente, preço descendente e nome descendente, e que a opção ativa é apresentada.

  @C01 @RN-ORD-02 @RN-ORD-03
  Cenário: C01 – Ordenar produtos por preço ascendente
    Dado Estou autenticado na loja Swag Labs e na página de catálogo de produtos
    Quando Escolho a ordenação "Price (low to high)" no seletor de ordenação
    Então Os seis produtos são apresentados do mais barato para o mais caro, com os preços por ordem crescente: $7.99, $9.99, $15.99, $15.99, $29.99, $49.99
    E A opção ativa do seletor é "Price (low to high)"
    E A verificação incide sobre a sequência de preços e não sobre a posição relativa dos produtos com o mesmo preço de $15.99

  @C02 @RN-ORD-02 @RN-ORD-03
  Cenário: C02 – Ordenar produtos por preço descendente
    Dado Estou autenticado na loja Swag Labs e na página de catálogo de produtos
    Quando Escolho a ordenação "Price (high to low)" no seletor de ordenação
    Então Os seis produtos são apresentados do mais caro para o mais barato, com os preços por ordem decrescente: $49.99, $29.99, $15.99, $15.99, $9.99, $7.99
    E A opção ativa do seletor é "Price (high to low)"
    E A verificação incide sobre a sequência de preços e não sobre a posição relativa dos produtos com o mesmo preço de $15.99

  @C03 @RN-ORD-02
  Cenário: C03 – Ordenar produtos por nome descendente (Z a A)
    Dado Estou autenticado na loja Swag Labs e na página de catálogo de produtos
    Quando Escolho a ordenação "Name (Z to A)" no seletor de ordenação
    Então Os seis produtos são apresentados por ordem alfabética inversa: Test.allTheThings() T-Shirt (Red), Sauce Labs Onesie, Sauce Labs Fleece Jacket, Sauce Labs Bolt T-Shirt, Sauce Labs Bike Light, Sauce Labs Backpack
    E A opção ativa do seletor é "Name (Z to A)"
