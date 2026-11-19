# language: pt
@QAAGENT-3
Funcionalidade: Validação de campos obrigatórios no formulário de login
  Verificar que o formulário de login apresenta a mensagem de erro correta para cada campo obrigatório em falta e que o utilizador permanece na página de login.

  @C01 @RN-LOGIN-03
  Cenário: C01 – Submeter login sem preencher nenhum campo
    Dado O utilizador está na página de login
    Quando O utilizador submete o formulário de login sem preencher o utilizador nem a password
    Então É apresentada a mensagem de erro indicando que o utilizador é obrigatório
    E A mensagem de erro não indica que a password é obrigatória
    E O utilizador permanece na página de login

  @C02 @RN-LOGIN-03 @RN-LOGIN-04
  Cenário: C02 – Submeter login apenas com utilizador preenchido
    Dado O utilizador está na página de login
    Quando O utilizador preenche o campo utilizador com 'standard_user'
    E O utilizador deixa o campo password vazio
    E O utilizador submete o formulário de login
    Então É apresentada a mensagem de erro indicando que a password é obrigatória
    E O utilizador permanece na página de login
