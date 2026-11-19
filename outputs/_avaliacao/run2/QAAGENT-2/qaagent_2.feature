# language: pt
@QAAGENT-2
Funcionalidade: Bloqueio de acesso a utilizador com conta bloqueada
  Validar que uma conta bloqueada não consegue iniciar sessão, que a mensagem de conta bloqueada é apresentada com o texto exato e que o utilizador a pode fechar.

  @C01 @RN-LOGIN-02
  Cenário: C01 – Login de conta bloqueada é recusado e mantém-se na página de login
    Dado O utilizador está na página de login da loja
    Quando Introduz o nome de utilizador de uma conta bloqueada
    E Introduz a password de teste
    E Submete o formulário de login
    Então O acesso à loja é recusado
    E O utilizador permanece na página de login
    E A página de produtos não é apresentada

  @C02 @RN-LOGIN-02
  Cenário: C02 – Mensagem de conta bloqueada é apresentada no login
    Dado O utilizador está na página de login da loja
    Quando Introduz o nome de utilizador de uma conta bloqueada
    E Introduz a password de teste
    E Submete o formulário de login
    Então É apresentada uma mensagem de erro
    E A mensagem indica que a conta se encontra bloqueada, com o texto exato: Epic sadface: Sorry, this user has been locked out

  @C03 @RN-LOGIN-06 @RN-LOGIN-02
  Cenário: C03 – Mensagem de erro de conta bloqueada pode ser fechada
    Dado O utilizador está na página de login da loja
    E Foi submetido o login de uma conta bloqueada e a mensagem de erro está apresentada
    Quando O utilizador fecha a mensagem de erro
    Então A mensagem de erro deixa de ser apresentada
    E O utilizador permanece na página de login
