# language: pt
@QAAGENT-3
Funcionalidade: Validação de campos obrigatórios no formulário de login
  Verificar que o formulário de login bloqueia a submissão com campos obrigatórios em falta, apresenta a mensagem de erro correta para cada campo e mantém o utilizador na página de login.

  @C01 @RN-LOGIN-03
  Cenário: C01 – Submeter login sem preencher nenhum campo
    Dado que o utilizador está na página de login
    E que os campos de utilizador e password estão vazios
    Quando o utilizador submete o formulário de login sem preencher nenhum campo
    Então é apresentada a mensagem de erro "Epic sadface: Username is required"
    E o utilizador permanece na página de login

  @C02 @RN-LOGIN-03 @RN-LOGIN-04
  Cenário: C02 – Submeter login apenas com o utilizador preenchido
    Dado que o utilizador está na página de login
    E que o campo de password está vazio
    Quando o utilizador preenche apenas o campo de utilizador com "standard_user"
    E o utilizador submete o formulário de login
    Então é apresentada a mensagem de erro "Epic sadface: Password is required"
    E o utilizador permanece na página de login
