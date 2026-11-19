# language: pt
@QAAGENT-2
Funcionalidade: Bloqueio de acesso a utilizador com conta bloqueada
  Validar que uma conta bloqueada não consegue iniciar sessão, que é apresentada a mensagem de conta bloqueada e que essa mensagem pode ser fechada pelo utilizador.

  @C01 @RN-LOGIN-02
  Cenário: C01 – Acesso recusado a conta bloqueada
    Dado Que estou na página de login da loja
    Quando Introduzo o utilizador de uma conta bloqueada e a respetiva password
    E Submeto o formulário de login
    Então O acesso à loja é recusado
    E Permaneço na página de login

  @C02 @RN-LOGIN-02
  Cenário: C02 – Mensagem de erro de conta bloqueada apresentada
    Dado Que estou na página de login da loja
    Quando Introduzo o utilizador de uma conta bloqueada e a respetiva password
    E Submeto o formulário de login
    Então É apresentada uma mensagem de erro com o texto 'Epic sadface: Sorry, this user has been locked out.'

  @C03 @RN-LOGIN-06 @RN-LOGIN-02
  Cenário: C03 – Fecho da mensagem de conta bloqueada
    Dado Que estou na página de login da loja
    E Que a mensagem de erro de conta bloqueada está apresentada após uma tentativa de login com a conta bloqueada
    Quando Utilizo o botão de fechar a mensagem de erro
    Então A mensagem de erro deixa de ser apresentada
    E Permaneço na página de login
