# language: pt
@QAAGENT-3
Funcionalidade: Validação de campos obrigatórios no formulário de login
  Validar que o formulário de login apresenta a mensagem de erro correta quando o utilizador ou a password não são preenchidos e que o utilizador permanece na página de login.

  @C01 @RN-LOGIN-03 @RN-LOGIN-04
  Cenário: C01 – Submeter login sem preencher nenhum campo
    Dado O utilizador está na página de login
    Quando O utilizador submete o formulário de login sem preencher o utilizador nem a password
    Então É apresentada a mensagem de erro "Epic sadface: Username is required"
    E O utilizador permanece na página de login

  @C02 @RN-LOGIN-03 @RN-LOGIN-04
  Cenário: C02 – Submeter login apenas com o utilizador preenchido
    Dado O utilizador está na página de login
    Quando O utilizador preenche o campo utilizador com "standard_user"
    E O utilizador submete o formulário de login sem preencher a password
    Então É apresentada a mensagem de erro "Epic sadface: Password is required"
    E O utilizador permanece na página de login
