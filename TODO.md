# Roteiro do Projeto - Foco: Módulo de Despesas


Este roteiro detalha as tarefas para o desenvolvimento e aperfeiçoamento do módulo de despesas do projeto, utilizando a aplicação `despesa-api-mvp` e com base nos modelos e requisitos definidos.


## Fase 1: Análise e Desenho do Módulo


Objetivo: Definir a estrutura de dados, regras de negócio e fluxos de interação para o controle de despesas.


- [x] **Análise de Requisitos Funcionais:**
   - [x] Levantar as necessidades de auditoria e controle da COGEX. _(concluído em `tech/subs/contas/README.md`)_
   - [x] Definir o fluxo de submissão e aprovação de despesas (ciclo de vida da auditoria).
   - [x] Especificar os requisitos para relatórios e estatísticas. _(concluído em `tech/requisitos-relatorios.md`)_
- [x] **Estrutura de Dados (Data Modeling):**
   - [x] Criar o modelo de dados para uma `Despesa`. _(concluído em `tech/subs/contas/Modelo-Inicial-Despesas.md`)_
   - [x] Desenvolver e manter uma lista padronizada e gerenciável de `Categorias` e `Subcategorias` de despesas.
   - [x] Modelar a entidade para `Comprovantes` (arquivos/documentos).
   - [x] Modelar a entidade para `Solicitacoes de Esclarecimento` ou `InteracoesAuditoria`.
- [x] **Mapeamento de Entidades na API:**
   - [x] Revisar e expandir os modelos existentes (`Credor`, `Exercicio`, `Fonte`, `Orgao`) e criar os novos (`Despesa`, `Categoria`, etc.) na aplicação `despesa-api-mvp`.
- [x] **Desenho da Arquitetura e Fluxos:**
   - [x] Desenhar o fluxo de dados completo: `Serventia -> API -> Auditoria`.
   - [x] Projetar a interação para solicitação de novas categorias de despesa. _(concluído em `tech/fluxo-solicitacao-categoria.md`)_


## Fase 2: Desenvolvimento do Backend (`despesa-api-mvp`)


Objetivo: Implementar a lógica de negócio e os endpoints da API de despesas.


- [x] **Configuração do Ambiente:**
   - [x] Garantir que o ambiente de desenvolvimento (Docker, Maven, Banco de Dados) esteja funcional.
- [x] **Endpoints CRUD para Entidades Principais:**
   - [x] CRUD para `Despesas`.
   - [x] CRUD para `Categorias` e `Subcategorias` (com acesso restrito para administradores/COGEX).
   - [x] Endpoint para upload e associação de `Comprovantes`.
   - [x] Implementar a lógica de armazenamento de arquivos para `Comprovantes`.
- [x] **Implementação da Lógica de Negócio (Workflows):**
   - [x] Implementar o ciclo de vida do status da despesa (`Registrada`, `Submetida`, `Aprovada`, `Rejeitada`, `Pendente de Esclarecimento`).
   - [x] Desenvolver o endpoint para auditores solicitarem esclarecimentos sobre uma despesa.
   - [x] Criar a funcionalidade para uma serventia responder a uma solicitação de esclarecimento.
   - [x] Implementar o sistema de notificação para novas categorias de despesa solicitadas. _(Implementado com envio de email para o admin)_
- [x] **Endpoints de Relatórios e Controle:**
   - [x] Criar endpoint que gere relatórios com estatísticas (despesas revisadas, negadas, aceitas, etc.). _(endpoint inicial implementado em `RelatorioController`)_
   - [x] Implementar a funcionalidade para desabilitar/habilitar tipos de despesa para uma ou todas as serventias, com registro do motivo. _(Backend API e lógica de validação implementados)_
- [x] **Segurança e Testes:**
   - [x] Implementar autenticação e autorização baseada em papéis (ex: `ROLE_SERVENTIA`, `ROLE_AUDITOR`, `ROLE_ADMIN`).
   - [x] Escrever testes unitários e de integração para todos os endpoints e lógicas de negócio. _(Testes para feature RegraDespesa implementados)_


## Fase 3: Desenvolvimento da Interface do Usuário (`despesas-front-mvp`)


Objetivo: Criar as interfaces para que serventias e auditores possam interagir com o sistema.


- [x] **Estrutura e Navegação:**
   - [x] Configurar rotas e layout principal da aplicação. _(implementado em `app/layout.tsx`)_
   - [x] Criar um componente de navegação (Navbar) com links para as áreas principais (Despesas, Admin). _(implementado em `components/Navbar.tsx`)_
   - [x] Implementar a lógica de autenticação e rotas protegidas. _(implementado com `LoginForm` e `AuthContext`)_
- [x] **Interface da Serventia:**
   - [x] Tela para registro e edição de novas despesas (`status = 'Registrada'`). _(implementado com `DespesaForm.tsx`)_
   - [x] Galeria de comprovantes associados a uma despesa. _(Upload implementado em `DespesaForm`, visualização na tela de detalhes `despesas/[id]`)_
   - [x] Painel para visualizar o status de todas as despesas submetidas. _(implementado em `DespesasList.tsx`)_
   - [x] Interface para responder a solicitações de esclarecimento da auditoria. _(Implementado com `ResponderEsclarecimentoModal`)_
   - [x] Formulário para solicitar a criação de uma nova categoria de despesa. _(Implementado com `SolicitarCategoriaModal`)_
- [x] **Interface da Auditoria (COGEX):**
   - [x] Painel com a fila de despesas submetidas (`status = 'Submetida'`). _(visualização implementada em `DespesasList.tsx` com base no role)_
   - [x] Tela de análise com visão lado a lado da despesa e seu comprovante. _(Implementado em `despesas/[id]/page.tsx`)_
   - [x] Ações na tela de análise: `Aprovar`, `Rejeitar` (com justificativa), `Solicitar Esclarecimento`. _(botões de ação implementados em `DespesasList.tsx`)_
   - [x] Painel para gerenciamento de `Categorias` e `Subcategorias`. _(Implementado em `AdminDashboard` com o componente `GerenciarCategorias`)_
   - [x] Interface para habilitar/desabilitar tipos de despesas. _(Implementado em `AdminDashboard` com o componente `GerenciarRegras`)_
   - [x] Dashboard com relatórios e estatísticas visuais. _(Implementado em `AdminDashboard` com o componente `Dashboard`)_


## Fase 4: Validação e Documentação


Objetivo: Assegurar a qualidade, a clareza e a prontidão do módulo.


- [x] **Documentação:**
   - [x] Gerar e manter a documentação da API (OpenAPI/Swagger).
   - [ ] Criar um manual de usuário simples para serventias e auditores.
- [ ] **Testes de Aceitação do Usuário (UAT):**
   - [ ] Realizar testes de aceitação com usuários-chave (Carol, Alcione) para validar os fluxos.
- [ ] **Implantação (Deployment):**
   - [ ] Preparar e documentar o processo de implantação da API e do Frontend.

popular as tabelas `Categoria` e `Subcategoria` do nosso sistema (via `data.sql`), para garantir a padronização.

## Atual para aprimoramento I

- [x] Ocultar o painel lateral se não estiver logado
- [x] Cadastro de serventias por RULE_COGEX_ADMIN (unico para todos os sistemas/modulos). O sistema atual sera substituido por Keycloak; manter flexibilidade para troca futura.
    - [x] Importar Serventias.txt (uma serventia por linha) e criar entidade ServentiaExtrajudicial com createdAt/updatedAt e colunas de dominio (backend).
    - [x] Importar Tipos_de_Cartorio.txt para entidade TIPO_DE_CARTORIO (backend).
    - [x] CRUD de ServentiaExtrajudicial com createdAt/updatedAt e colunas de dominio (backend).
    - [x] CRUD de TIPO_DE_CARTORIO (backend).
- [x] Relacionar ServentiaExtrajudicial <-> TIPO_DE_CARTORIO como funcao dinamica (adicao/remocao logica), com inicio/fim, quem aplicou, e historico consultavel. Apenas RULE_COGEX_ADMIN (backend).
    - [x] VINCULO SERV/TC deve registrar: data inicio/fim, quem aplicou/encerrou, motivo e comprovante em PDF obrigatorio (upload + armazenamento + auditoria).
        - [x] Adicionar campos no modelo (motivo, comprovantePdfPath/bytes, contentType, nomeArquivo).
        - [x] Exigir comprovante PDF nas rotas de vinculo/encerramento.
        - [x] Armazenar comprovante (arquivo ou blob) e expor endpoint seguro para download.
        - [x] Validar: sem PDF -> 400/422.
        - [x] O PDF deve ser salvo no servidor e com hash de conteúdo.
    - [x] O teste (devdocs/despesa-api-mvp.py) deve poder obter o download do pdf e o mesmo deve ser gravado em disco no mesmo diretório do script se não houver variável de ambiente DOWN_TESTE_FILES setada
        - [x] Criar PDF verdadeiros que podem conter as informações daquela despesa que está sendo enviada no teste, pode usar a lib fpdf2
  - [x] O endpoint GET /api/export/despesas.xlsx gera o XLSX em memória e retorna no response.
  - [x] Nenhum arquivo é salvo em disco pelo backend. Deve salvar em /app/uploads
  - [x] O teste apenas verifica status 200 e que o download aconteceu. Deve ser gravado em disco no mesmo diretório do script se não houver variável de ambiente DOWN_TESTE_FILES setada
    - [x] Teste deve salvar XLSX localmente quando DOWN_TESTE_FILES não estiver setada
    - [x] Se DOWN_TESTE_FILES estiver setada, apenas validar status/bytes
    - [x] Definir convenção de nome do arquivo salvo (ex.: despesas_<timestamp>.xlsx)
    - [x] Salvar CSV (separador ;) e ODS em /app/uploads para compatibilidade.

- [x] Indicar delegatario da serventia (por hora direto do banco), apenas RULE_COGEX_ADMIN (backend).
- [x] Auditoria com filtros por ServentiaExtrajudicial, por ServentiaExtrajudicial/TIPO_DE_CARTORIO e por MES/ANO (padrao: mes/ano atual) (backend).
- [x] Cadastro de usuarios vinculado a serventia + perfil (RULEs) + dominio (backend):
    - [x] RULE_CARTARIO_TITULAR=1, RULE_CARTARIO_INTERINO=2, RULE_CARTARIO_SUBSTITUTO=3, RULE_CARTARIO_APOIO=5.
    - [x] Revisar nomenclaturas para padrao unico no core (backend).
- [x] Regras de permissao baseadas nos itens acima:
    - [x] Quem pode `lancar despesas` >= RULE_CARTARIO_APOIO (backend).
    - [x] Quem pode `aprovar edicao` >= RULE_CARTARIO_APOIO (backend via PUT /api/despesas/{id}).
    - [x] Quem pode `enviar para COGEX` <= RULE_CARTARIO_SUBSTITUTO (3) (backend).

## Atual para aprimoramento II

- [x] UI sprint: telas de Serventias, Tipos de Cartorio e Usuarios (frontend).
- [x] Persistir estado do filtro atual e so atualizar apos novo filtro ser setado (frontend).
- [x] Mudar todas as referências de ID por descrição, nome ou label em vários formulários que pede a ID ao invés do label ou nome
    - [x] Indicar a serventia
    - [x] Indicar a categoria
    - [x] Seguir a heurística em todo o sistema web, se emcontrar uma possível case, relatar

## Atual para aprimoramento III

- [-] Deve conter a nota da compra em pdf (a despesa não pode ser cadastrada sem esse documento) 
    - [ ] Obrigatório salvar no banco de dados e retornar em formato que a interface web possa exibir diretamente na tela e não só baixar
- [ ] Deve conter o comprovante de pagamento BB ou CAIXA (Suporte iniciais)

## Fase 5: Features Futuras

- [ ] Criar classes que precisam de aprovação prévia da COGEX para serem empenhadas, de tal modo que terá que ser apresentada, via link no próprio sistema do processo aprovado (solicitação e ok, algo simples por clicks) Exigirá então uma página própria e uma fluxo próprio, não será possível o gasto sem permissão inicial.
- [ ] Ícones destacados de Tarefas que indica que há despeas para revisar
- [ ] Ícones destacados de Tarefas que indica que há despeas para avaliar/auditar/aprovar-rejeitar-pedir_esclarecimento
- [ ] Qualquer tipo de gastos pode ser bloqueados numa serventia ou en todas, passa a valer no dia seguinte

## Bugfixes

### Login de usuários além do in-memory

- [x] Deve permitir acesso dos usuários na tabela usuario_dominio conforme as ROLEs de lá e os passwords de lá também

### UI

- [ ] http://localhost:3001/solicitacoes-categoria tem botão desproporcional e está muito grande.
- [-] Despesas deve ter dois PDFs, um para a nota fiscal e outro para o comprovante de pagamento. No momento, só há para o último. Atualise o teste devdocs/despesa-api-mvp.py e UI


### Acesso

- [ ] Ao clicar em despesas está vindo de todas as serventias e deveria vir apenas as da serventia do usuário, caso o mesmo tenha acesso

## ModelFixes

- [ ] despesa não depende de tipo_cartorio_id, confirmar e remover se for o caso
- [ ] usuario_dominio poderia ir e voltar, para isso, é preciso ter uma ligação ao invé de acesso direto
- [ ] despesa não depende de categoria_id, subcategoria_id basta
- [ ] despesa não precisa categoria_id
- [ ] despesa depende de solicitacao_esclarecimento.id, está ao contrário, confirmar e ajustar se for o caso
- [ ] despesa depende de comprovante.id, está ao contrário, confirmar e ajustar se for o caso
- [ ] regra_despesa não depende de categoria.id, confirmar e remover se for o caso
- [ ] mudar RULE_ para ROLE_ 

## UIFixes

- [ ] Em Navbar "Painel" está 'email · RULE_CARTORIO_APOIO'  deve ser 'Serventia · email · RULE_CARTORIO_APOIO' 
- [x] No menu lateral que chama http://localhost:3001/despesas/nova, subcategorias e categorias também não renderizaram nas listas de seleção
- [ ] Ao clicar no link para baixar o o comprovante está ocorrendo um redirecionanmento que está solicitando usuário e senha novamente num popup numa primeira vez na sessão e apesar de não ser impeditivo, deve ser resolvido e entendido o porquê, para domínio do sistema e tecnologia, e apesar de baixar o arquivo, após fornecer usuário e senha, isso quebra a experiencia do usuário. Isso deve ser corrigido pra ser entregue diretamente pela aplicação web.
- [ ] Em http://localhost:3001/despesas deve aparecer mais duas colunas, 'Nt Fiscal' e 'Comprovante' e as entradas possuem links para seu arquivos
- [ ] /despesas/nova está adicionandod apenas um documento e sem dizer o tipo dele se é Nota ou Comprovante e deve permitir já adicionar dois arquivos e a única verificação é que não sejam do mesmo tipo e nem o mesmo arquivo. A despesa pode ser criada inicialmente sem tais arquivos
    - [ ] Dito isso, então é obrigatório em algum momento ter a opção de adicionar tais documentos, ao clicar em detalhes, na lista de despesas é um bom lugar para esse retorno visual
    - [ ] Assim, cabe o aprimoramento visual da lista de despesas essa indicaçõe dos estados de tais arquivos para alertar sobre a necessidade e a tarefa antess que a mesma fique pronta para submeter, este controle já existe e exige ambos ao tentar submeter, a propósito. 

## Security

- [ ] Checar validação de todas interações (elementos obrigatório e entradas de informação/segurança da informação)



