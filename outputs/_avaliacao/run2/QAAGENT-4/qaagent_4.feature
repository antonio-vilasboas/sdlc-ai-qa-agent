# language: pt
@QAAGENT-4
Funcionalidade: Ordenação de produtos no catálogo
  Validar que o cliente autenticado consegue ordenar os produtos do catálogo por preço ascendente, preço descendente e nome descendente, com a opção ativa corretamente indicada.

  @C01 @RN-ORD-02 @RN-ORD-03
  Cenário: C01 – Ordenar catálogo por preço ascendente
    Dado Estou autenticado na loja Swag Labs
    E Estou na página de catálogo de produtos
    Quando Escolho a ordenação por preço ascendente no seletor de ordenação
    Então Os seis produtos são apresentados do mais barato para o mais caro
    E A sequência de preços apresentada é $7.99, $9.99, $15.99, $15.99, $29.99, $49.99
    E A opção ativa do seletor apresenta 'Price (low to high)'

  @C02 @RN-ORD-02 @RN-ORD-03
  Cenário: C02 – Ordenar catálogo por preço descendente
    Dado Estou autenticado na loja Swag Labs
    E Estou na página de catálogo de produtos
    Quando Escolho a ordenação por preço descendente no seletor de ordenação
    Então Os seis produtos são apresentados do mais caro para o mais barato
    E A sequência de preços apresentada é $49.99, $29.99, $15.99, $15.99, $9.99, $7.99
    E A opção ativa do seletor apresenta 'Price (high to low)'

  @C03 @RN-ORD-02
  Cenário: C03 – Ordenar catálogo por nome descendente (Z a A)
    Dado Estou autenticado na loja Swag Labs
    E Estou na página de catálogo de produtos
    Quando Escolho a ordenação por nome descendente (Z a A) no seletor de ordenação
    Então Os seis produtos são apresentados por ordem alfabética inversa dos nomes
    E A sequência de nomes apresentada é Test.allTheThings() T-Shirt (Red), Sauce Labs Onesie, Sauce Labs Fleece Jacket, Sauce Labs Bolt T-Shirt, Sauce Labs Bike Light, Sauce Labs Backpack
    E A opção ativa do seletor apresenta 'Name (Z to A)'
