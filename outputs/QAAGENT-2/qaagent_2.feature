# language: pt
@QAAGENT-2
Funcionalidade: Bloqueio de acesso a utilizador com conta bloqueada
  Validar que uma conta bloqueada não consegue iniciar sessão, que o utilizador permanece na página de login com a mensagem de conta bloqueada, e que essa mensagem pode ser fechada.

  @C01 @RN-LOGIN-02
  Cenário: C01 – Acesso recusado a conta bloqueada e permanência no login
    Dado Estou na página de login da loja Swag Labs
    Quando Introduzo o utilizador da conta bloqueada e a respetiva password
    E Submeto o formulário de login
    Então O acesso à loja é recusado
    E Permaneço na página de login (/)
    E Não sou redirecionado para a página de produtos

  @C02 @RN-LOGIN-02
  Cenário: C02 – Mensagem de conta bloqueada apresentada no login
    Dado Estou na página de login da loja Swag Labs
    Quando Introduzo o utilizador da conta bloqueada e a respetiva password
    E Submeto o formulário de login
    Então É apresentada uma mensagem de erro
    E A mensagem indica que a conta se encontra bloqueada, com o texto exato 'Epic sadface: Sorry, this user has been locked out.'

  @C03 @RN-LOGIN-06 @RN-LOGIN-02
  Cenário: C03 – Fecho da mensagem de erro de conta bloqueada
    Dado Estou na página de login da loja Swag Labs
    E Tentei autenticar-me com a conta bloqueada e a mensagem de erro de conta bloqueada está apresentada
    Quando Aciono o botão de fecho da mensagem de erro
    Então A mensagem de erro deixa de estar visível
    E Permaneço na página de login (/)
