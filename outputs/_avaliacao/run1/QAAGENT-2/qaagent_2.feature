# language: pt
@QAAGENT-2
Funcionalidade: Bloqueio de acesso a utilizador com conta bloqueada
  Validar que uma conta bloqueada não consegue iniciar sessão, que é apresentada a mensagem de conta bloqueada e que essa mensagem pode ser fechada.

  @C01 @RN-LOGIN-02
  Cenário: C01 – Acesso recusado a conta bloqueada no login
    Dado Estou na página de login da loja
    Quando Introduzo o utilizador de teste de conta bloqueada e a password de teste
    E Submeto o formulário de login
    Então O acesso à loja é recusado
    E Permaneço na página de login (/)
    E Não sou redirecionado para o catálogo de produtos

  @C02 @RN-LOGIN-02
  Cenário: C02 – Mensagem de conta bloqueada apresentada no login
    Dado Estou na página de login da loja
    Quando Introduzo o utilizador de teste de conta bloqueada e a password de teste
    E Submeto o formulário de login
    Então É apresentada uma mensagem de erro
    E A mensagem de erro apresentada é exatamente "Epic sadface: Sorry, this user has been locked out."
    E Permaneço na página de login

  @C03 @RN-LOGIN-06 @RN-LOGIN-02
  Cenário: C03 – Fecho da mensagem de conta bloqueada
    Dado Estou na página de login da loja
    E Tentei iniciar sessão com o utilizador de teste de conta bloqueada e a password de teste
    E A mensagem de conta bloqueada está apresentada
    Quando Fecho a mensagem de erro através do botão de fecho
    Então A mensagem de erro deixa de ser apresentada
    E Permaneço na página de login
