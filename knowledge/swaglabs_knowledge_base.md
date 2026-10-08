# Swag Labs – Base de Conhecimento QA

## 0. Âmbito e Convenções

Aplicação: Swag Labs — https://www.saucedemo.com

Âmbito: fluxos cobertos pelas User Stories QAAGENT-1 a QAAGENT-6 (autenticação, catálogo, ordenação, carrinho, checkout e sessão).

Estratégia de seletores: usar exclusivamente o atributo `data-test`, no formato `[data-test="<valor>"]`. Não usar XPath nem classes CSS. Em Playwright (Python): `page.locator('[data-test="<valor>"]')`.

Origem da informação: seletores e mensagens recolhidos manualmente na aplicação real (Chrome DevTools); regras de negócio revistas e aprovadas pelo autor.

Data da última revisão: 08/10/2026 (v2: RN-ORD-03 revista; padrão remove-<produto> qualificado)

## 1. Utilizadores de Teste

As credenciais de teste são públicas e apresentadas na própria página de login da aplicação.

| Utilizador | Password | Comportamento esperado | User Stories |
| --- | --- | --- | --- |
| `standard_user` | `secret_sauce` | Acesso normal à loja | QAAGENT-1, QAAGENT-4, QAAGENT-5, QAAGENT-6 |
| `locked_out_user` | `secret_sauce` | Acesso recusado: conta bloqueada | QAAGENT-2 |

Os restantes utilizadores listados na página de login (`problem_user`, `performance_glitch_user`, `error_user`, `visual_user`) estão fora do âmbito.

## 2. Ecrã de Login

URL: `/` (https://www.saucedemo.com/)

| Elemento | data-test | Tipo | Observações |
| --- | --- | --- | --- |
| Campo utilizador | `username` | input | Placeholder "Username" |
| Campo password | `password` | input | Placeholder "Password" |
| Botão de login | `login-button` | input (submit) | Texto "Login" |
| Mensagem de erro | `error` | h3 | Só existe no DOM após um erro de validação |
| Botão fechar erro | `error-button` | button | Dentro da mensagem de erro |
| Credenciais de teste | `login-credentials` | div | Lista de utilizadores aceites |
| Password de teste | `login-password` | div | Password comum a todos os utilizadores |

Regras de negócio do login:

- RN-LOGIN-01: Com credenciais válidas, o utilizador é redirecionado para `/inventory.html` e o título da página é "Products".
- RN-LOGIN-02: Com uma conta bloqueada, o acesso é recusado, o utilizador permanece em `/` e é apresentada a mensagem de conta bloqueada.
- RN-LOGIN-03: O utilizador é obrigatório; é validado antes da password.
- RN-LOGIN-04: A password é obrigatória.
- RN-LOGIN-05: Credenciais que não correspondem a nenhum utilizador são recusadas com mensagem própria.
- RN-LOGIN-06: Qualquer mensagem de erro pode ser fechada através do botão `error-button`.

Mensagens do login (texto exato):

| Situação | Texto exato |
| --- | --- |
| Utilizador em falta | `Epic sadface: Username is required` |
| Password em falta | `Epic sadface: Password is required` |
| Credenciais inválidas | `Epic sadface: Username and password do not match any user in this service` |
| Conta bloqueada | `Epic sadface: Sorry, this user has been locked out.` |

## 3. Catálogo de Produtos

URL: `/inventory.html`

| Elemento | data-test | Tipo | Observações |
| --- | --- | --- | --- |
| Título da página | `title` | span | Texto "Products" |
| Seletor de ordenação | `product-sort-container` | select | Ver secção 4 |
| Opção de ordenação ativa | `active-option` | span | Texto da opção selecionada |
| Lista de produtos | `inventory-list` | div | Contém os 6 produtos |
| Cartão de produto | `inventory-item` | div | Um por produto |
| Nome do produto | `inventory-item-name` | div | |
| Descrição do produto | `inventory-item-desc` | div | |
| Preço do produto | `inventory-item-price` | div | Formato `$29.99` |
| Botão adicionar ao carrinho | `add-to-cart-<produto>` | button | Ex.: `add-to-cart-sauce-labs-backpack` |
| Botão remover do carrinho | `remove-<produto>` | button | Substitui o botão de adicionar após adicionar o produto |
| Ícone do carrinho | `shopping-cart-link` | a | Abre `/cart.html` |
| Contador do carrinho | `shopping-cart-badge` | span | Só existe no DOM com pelo menos 1 artigo |

O sufixo `<produto>` dos botões corresponde ao nome do produto em minúsculas, com espaços substituídos por hífenes (ver tabela de produtos). O padrão `add-to-cart-<produto>` foi observado nos 6 produtos; o padrão `remove-<produto>` foi observado nos produtos Sauce Labs Backpack e Sauce Labs Bike Light e assume-se igual para os restantes.

Produtos disponíveis (ordem por omissão):

| Nome | Preço | Sufixo `<produto>` |
| --- | --- | --- |
| Sauce Labs Backpack | $29.99 | `sauce-labs-backpack` |
| Sauce Labs Bike Light | $9.99 | `sauce-labs-bike-light` |
| Sauce Labs Bolt T-Shirt | $15.99 | `sauce-labs-bolt-t-shirt` |
| Sauce Labs Fleece Jacket | $49.99 | `sauce-labs-fleece-jacket` |
| Sauce Labs Onesie | $7.99 | `sauce-labs-onesie` |
| Test.allTheThings() T-Shirt (Red) | $15.99 | `test.allthethings()-t-shirt-(red)` |

## 4. Ordenação do Catálogo

URL: `/inventory.html` — seletor `[data-test="product-sort-container"]`

| Opção visível | Valor (value) | Resultado esperado |
| --- | --- | --- |
| Name (A to Z) | `az` | Nomes por ordem alfabética crescente |
| Name (Z to A) | `za` | Nomes por ordem alfabética decrescente |
| Price (low to high) | `lohi` | Preços por ordem crescente |
| Price (high to low) | `hilo` | Preços por ordem decrescente |

Regras de negócio da ordenação:

- RN-ORD-01: A ordenação por omissão é "Name (A to Z)" (`az`).
- RN-ORD-02: A opção ativa é apresentada no elemento `active-option`.
- RN-ORD-03: A ordem relativa entre produtos com o mesmo preço não está especificada (ex.: Sauce Labs Bolt T-Shirt e Test.allTheThings() T-Shirt (Red), ambos a $15.99). As validações de ordenação por preço devem verificar a sequência de preços e não a posição de produtos com preço igual.

## 5. Carrinho de Compras

URL: `/cart.html`

| Elemento | data-test | Tipo | Observações |
| --- | --- | --- | --- |
| Título da página | `title` | span | Texto "Your Cart" |
| Lista do carrinho | `cart-list` | div | |
| Artigo no carrinho | `inventory-item` | div | Um por produto adicionado |
| Nome do artigo | `inventory-item-name` | div | |
| Preço do artigo | `inventory-item-price` | div | |
| Quantidade | `item-quantity` | div | |
| Botão remover | `remove-<produto>` | button | Mesmo padrão do catálogo |
| Continuar a comprar | `continue-shopping` | button | Regressa ao catálogo |
| Iniciar checkout | `checkout` | button | Abre `/checkout-step-one.html` |

Regras de negócio do carrinho:

- RN-CART-01: O contador `shopping-cart-badge` indica o número de produtos distintos no carrinho (1 após adicionar um produto, 2 após adicionar um segundo).
- RN-CART-02: Quando o carrinho está vazio, o contador não é apresentado (o elemento não existe no DOM).
- RN-CART-03: Ao adicionar um produto, o botão `add-to-cart-<produto>` é substituído por `remove-<produto>`.
- RN-CART-04: Remover um produto no carrinho retira-o da lista e decrementa o contador.
- RN-CART-05: Cada produto é adicionado com quantidade 1.

## 6. Checkout – Informação do Cliente

URL: `/checkout-step-one.html`

| Elemento | data-test | Tipo | Observações |
| --- | --- | --- | --- |
| Título da página | `title` | span | Texto "Checkout: Your Information" |
| Primeiro nome | `firstName` | input | Placeholder "First Name" |
| Apelido | `lastName` | input | Placeholder "Last Name" |
| Código postal | `postalCode` | input | Placeholder "Zip/Postal Code" |
| Continuar | `continue` | input (submit) | Avança para `/checkout-step-two.html` |
| Cancelar | `cancel` | button | Regressa ao carrinho |
| Mensagem de erro | `error` | h3 | Só existe no DOM após um erro de validação |

Regras de negócio da informação do cliente:

- RN-CHK-01: Os três campos (primeiro nome, apelido, código postal) são obrigatórios; sem eles não é possível avançar para o resumo.
- RN-CHK-02: A validação é feita pela ordem primeiro nome → apelido → código postal, sendo apresentada apenas a mensagem do primeiro campo em falta.

Mensagens da informação do cliente (texto exato):

| Situação | Texto exato |
| --- | --- |
| Primeiro nome em falta | `Error: First Name is required` |
| Apelido em falta | `Error: Last Name is required` |
| Código postal em falta | `Error: Postal Code is required` |

## 7. Checkout – Resumo da Encomenda

URL: `/checkout-step-two.html`

| Elemento | data-test | Tipo | Observações |
| --- | --- | --- | --- |
| Título da página | `title` | span | Texto "Checkout: Overview" |
| Artigo da encomenda | `inventory-item` | div | Um por produto |
| Nome do artigo | `inventory-item-name` | div | |
| Preço do artigo | `inventory-item-price` | div | |
| Informação de pagamento | `payment-info-value` | div | Texto "SauceCard #31337" |
| Informação de envio | `shipping-info-value` | div | Texto "Free Pony Express Delivery!" |
| Subtotal | `subtotal-label` | div | Formato `Item total: $29.99` |
| Taxa | `tax-label` | div | Formato `Tax: $2.40` |
| Total | `total-label` | div | Formato `Total: $32.39` |
| Finalizar | `finish` | button | Abre `/checkout-complete.html` |
| Cancelar | `cancel` | button | Regressa ao catálogo |

Regras de negócio do resumo:

- RN-CHK-03: O subtotal ("Item total") é a soma dos preços dos artigos da encomenda.
- RN-CHK-04: A taxa corresponde a 8% do subtotal, arredondada a 2 casas decimais (ex.: subtotal $29.99 → taxa $2.40).
- RN-CHK-05: O total é igual à soma do subtotal com a taxa (ex.: $29.99 + $2.40 = $32.39).

## 8. Checkout – Confirmação

URL: `/checkout-complete.html`

| Elemento | data-test | Tipo | Observações |
| --- | --- | --- | --- |
| Título da página | `title` | span | Texto "Checkout: Complete!" |
| Cabeçalho de confirmação | `complete-header` | h2 | |
| Texto de confirmação | `complete-text` | div | |
| Voltar aos produtos | `back-to-products` | button | Regressa ao catálogo |

Regras de negócio da confirmação:

- RN-CHK-06: Após finalizar, é apresentada a confirmação da encomenda e o carrinho fica vazio (o contador deixa de ser apresentado).

Mensagens da confirmação (texto exato):

| Situação | Texto exato |
| --- | --- |
| Cabeçalho | `Thank you for your order!` |
| Texto | `Your order has been dispatched, and will arrive just as fast as the pony can get there!` |

## 9. Menu Lateral e Sessão

Disponível em todas as páginas após autenticação.

| Elemento | data-test | Tipo | Observações |
| --- | --- | --- | --- |
| Abrir menu | `open-menu` | img | Ícone ☰ no canto superior esquerdo |
| Fechar menu | `close-menu` | img | |
| Todos os produtos | `inventory-sidebar-link` | a | |
| Terminar sessão | `logout-sidebar-link` | a | Regressa a `/` |
| Repor estado da aplicação | `reset-sidebar-link` | a | Esvazia o carrinho |

Os itens do menu existem no DOM mesmo com o menu fechado, mas só são clicáveis depois de abrir o menu (`open-menu`).

Regras de negócio da sessão:

- RN-SES-01: Após terminar sessão, o utilizador regressa à página de login (`/`).
- RN-SES-02: Aceder diretamente a uma página interna sem sessão iniciada redireciona para `/` e apresenta uma mensagem de erro.

Mensagens da sessão (texto exato):

| Situação | Texto exato |
| --- | --- |
| Acesso ao catálogo sem sessão | `Epic sadface: You can only access '/inventory.html' when you are logged in.` |

## 10. Rastreabilidade User Story → Regras

| User Story | Secções | Regras |
| --- | --- | --- |
| QAAGENT-1 | 1, 2, 3 | RN-LOGIN-01 |
| QAAGENT-2 | 1, 2 | RN-LOGIN-02, RN-LOGIN-06 |
| QAAGENT-3 | 2 | RN-LOGIN-03, RN-LOGIN-04 |
| QAAGENT-4 | 3, 4 | RN-ORD-01, RN-ORD-02, RN-ORD-03 |
| QAAGENT-5 | 3, 5 | RN-CART-01 a RN-CART-05 |
| QAAGENT-6 | 2, 3, 5, 6, 7, 8 | RN-LOGIN-01, RN-CART-01, RN-CHK-01 a RN-CHK-06 |
