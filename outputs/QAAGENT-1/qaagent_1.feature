# language: pt
@QAAGENT-1
Funcionalidade: Autenticação de utilizador com credenciais válidas
  Validar que um cliente registado com credenciais válidas acede ao catálogo de produtos, com o título da secção e a lista de produtos visíveis.

  @C01 @RN-LOGIN-01
  Cenário: C01 – Login com credenciais válidas redireciona para o catálogo
    Dado O utilizador está na página de login da aplicação
    Quando Introduz o utilizador válido no campo de utilizador
    E Introduz a password correspondente no campo de password
    E Submete o formulário de login
    Então O utilizador é redirecionado para a página de catálogo de produtos

  @C02 @RN-LOGIN-01
  Cenário: C02 – Título da secção de produtos visível após login
    Dado O utilizador autenticou-se com credenciais válidas e está na página de catálogo
    Quando Observa o título da secção de produtos
    Então O título da secção de produtos é visível
    E O título apresentado é "Products"

  @C03 @RN-LOGIN-01
  Cenário: C03 – Lista de produtos disponíveis apresentada após login
    Dado O utilizador autenticou-se com credenciais válidas e está na página de catálogo
    Quando Observa a lista de produtos disponíveis
    Então A lista de produtos é apresentada
    E A lista contém os 6 produtos disponíveis, com nome e preço
