# language: pt
@QAAGENT-4
Funcionalidade: Ordenação de produtos no catálogo
  Validar que o catálogo de produtos ordena corretamente por preço ascendente, preço descendente e nome descendente (Z a A), e que a opção ativa é apresentada no seletor.

  @C01 @RN-ORD-02 @RN-ORD-03
  Cenário: C01 – Ordenar produtos por preço ascendente
    Dado O cliente está autenticado e encontra-se na página de catálogo de produtos
    Quando O cliente seleciona a ordenação "Price (low to high)" no seletor de ordenação
    Então Os seis produtos são apresentados por ordem crescente de preço, do mais barato para o mais caro
    E Os preços apresentados, por ordem, são $7.99, $9.99, $15.99, $15.99, $29.99 e $49.99
    E A opção ativa do seletor de ordenação apresenta o texto "Price (low to high)"

  @C02 @RN-ORD-02 @RN-ORD-03
  Cenário: C02 – Ordenar produtos por preço descendente
    Dado O cliente está autenticado e encontra-se na página de catálogo de produtos
    Quando O cliente seleciona a ordenação "Price (high to low)" no seletor de ordenação
    Então Os seis produtos são apresentados por ordem decrescente de preço, do mais caro para o mais barato
    E Os preços apresentados, por ordem, são $49.99, $29.99, $15.99, $15.99, $9.99 e $7.99
    E A opção ativa do seletor de ordenação apresenta o texto "Price (high to low)"

  @C03 @RN-ORD-02
  Cenário: C03 – Ordenar produtos por nome descendente (Z a A)
    Dado O cliente está autenticado e encontra-se na página de catálogo de produtos
    Quando O cliente seleciona a ordenação "Name (Z to A)" no seletor de ordenação
    Então Os seis produtos são apresentados por ordem alfabética inversa de nome
    E A ordem apresentada é: Test.allTheThings() T-Shirt (Red), Sauce Labs Onesie, Sauce Labs Fleece Jacket, Sauce Labs Bolt T-Shirt, Sauce Labs Bike Light e Sauce Labs Backpack
    E A opção ativa do seletor de ordenação apresenta o texto "Name (Z to A)"
