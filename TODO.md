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

## Fase 5: Features Futuras

- [ ] Quanto aos arquivos de documentos, ambos devem seguir
    - [ ] Obrigatório salvar no banco de dados e retornar em formato que a interface web possa exibir diretamente na tela e não só baixar
    - [ ] Deve conter o comprovante de pagamento BB ou CAIXA (Suporte iniciais)
- [ ] Criar classes que precisam de aprovação prévia da COGEX para serem empenhadas, de tal modo que terá que ser apresentada, via link no próprio sistema do processo aprovado (solicitação e ok, algo simples por clicks) Exigirá então uma página própria e uma fluxo próprio, não será possível o gasto sem permissão inicial.
- [ ] Ícones destacados de Tarefas que indica que há despeas para revisar
- [ ] Ícones destacados de Tarefas que indica que há despeas para avaliar/auditar/aprovar-rejeitar-pedir_esclarecimento
- [ ] Qualquer tipo de gastos pode ser bloqueados numa serventia ou en todas, passa a valer no dia seguinte
- [ ] Mecanismo de confirmação dos dados das despesas
    - O visualizador tem uma versão alternativa de modo confronto, o usuário deve confirmar se a informação no painel corresponde ao conteúdo do PEF
    - O número de vezes que é necessário para permitir que a despesa seja livre para ser submetida é configurada pela COGEX, mas a princípio é '1' para todas as serventias
    - É o ponto principal para aumentar a garantia que uma despesa está de acordo com os documentos, isso faz com que seja possível reduzir o risco prestação errada enviada para a COGEX
        - Aumentar esta garantia é fundamental para o sistema alcançar sucesso esperado, reduzir o trabalho massante na COGEX
- [ ] No 'visão geral' o Dashboard deve ser mais interativo e gerar gráficos, cada card deve ser um link para o filtro indicado no memos
- [ ] Em /relatorios, acima de 'Entradas' adicionar dois ícones de exportar: um para o filtrado e outro por serventia
- [ ] Tipos de arquivos(imagens é mais fácil de manipular), tamanho e tempo de guarda no banco de dados e se será necessário manter por quanto tempo nas serventias tais arquivos
   - Uma vez as contas aprovadas, tá aprovado
- [ ] Habilitar 'Documentos' em menu para Serventias
   - [ ] Unificar componentes se possível

## Bugfixes

### Login de usuários além do in-memory

- [x] Deve permitir acesso dos usuários na tabela usuario_dominio conforme as ROLEs de lá e os passwords de lá também

### UI

- [x] /solicitacoes-categoria tem botão desproporcional e está muito grande.


### Acesso

- [x] Ao clicar em despesas está vindo de todas as serventias e deveria vir apenas as da serventia do usuário, caso o mesmo tenha acesso
- [x] Em 'Visão Geral' , na rota, /dashboard está vindo de todas as serventias e deveria vir apenas as da serventia do usuário, caso o mesmo tenha acesso
  - Isso está sendo detectado na UI, então o servidor está falhando nas permissões, pois estou com logado com user com o papel RULE_CARTORIO_TITULAR e verifiquei um com RULE_CARTORIO_APOIO e está acontecendo o mesmo

## ModelFixes

- Total Refactor:
   - [ ] Iniciar Flyway
   - [ ] Todas as tabelas que possuem campos do tipo xx_id deve ser modificadas para id_xx 
   - [ ] serventia_id está 'public.serventia_extrajudicial(id)', mas id_serventia é quem deve fazer essa referência
      - [ ] serventia_id deve ser retirada do modelo public.despesa
      - [ ] Isso deve refletir na nova devdocs/populate_data.py, testes em devdocs/despesa-api-mvp.py e despesa-api-mvp/src/test
      - [ ] ATENÇÃO só depois da de cima qualquer tabela do tipo id_xx se não tiver referência para uma tabela em sua definição então deve ser apagada
- [ ] despesa_id deve mudar para id_despesa
- [ ] despesa não depende de tipo_cartorio_id, confirmar e remover se for o caso
- [ ] usuario_dominio poderia ser demitido e recontratado, para isso, é preciso ter uma ligação ao invé de acesso direto
- [ ] despesa não depende de categoria_id, subcategoria_id basta
- [ ] despesa não precisa categoria_id
- [ ] despesa depende de solicitacao_esclarecimento.id, está ao contrário, confirmar e ajustar se for o caso
- [ ] despesa depende de comprovante.id, está ao contrário, confirmar e ajustar se for o caso
- [ ] regra_despesa não depende de categoria.id, confirmar e remover se for o caso

## UIFixes

- [x] Em Navbar "Painel" está 'email · RULE_CARTORIO_APOIO'  deve ser 'Serventia · email · Apoio' e assim pora os outros papeis 
- [x] No menu lateral que chama /despesas/nova, subcategorias e categorias também não renderizaram nas listas de seleção
- [x] Ao clicar no link para baixar o o comprovante está ocorrendo um redirecionanmento que está solicitando usuário e senha novamente num popup numa primeira vez na sessão e apesar de não ser impeditivo, deve ser resolvido e entendido o porquê, para domínio do sistema e tecnologia, e apesar de baixar o arquivo, após fornecer usuário e senha, isso quebra a experiencia do usuário. Isso deve ser corrigido pra ser entregue diretamente pela aplicação web.
- [x] Em /despesas deve aparecer mais duas colunas, 'Nt_Fiscal' e 'Comprovante' e as entradas possuem links para seu arquivos. Informe se se houve necessidade de mexher no modelo
- [x] /despesas/nova está adicionando apenas um documento e sem dizer o tipo dele se é Nota ou Comprovante e deve permitir já adicionar dois arquivos com seu tipo
    - [x] A única verificação é que não sejam do mesmo tipo e nem o mesmo arquivo. A despesa pode ser criada inicialmente sem tais arquivos
    - [x] Dito isso, então é obrigatório em algum momento ter a opção de adicionar tais documentos, ao clicar em detalhes, na lista de despesas é um bom lugar para esse retorno visual
      - [x] Mas também é preciso dizer o tipo de documento que está sendo enviado em detales, no momento, mesmo enviando dois arquivos por lá, ambos são enviados como COMPROVANTE_PAGAMENTO
    - [x] Assim, cabe o aprimoramento visual da lista de despesas, essas indicações dos estados dos arquivos para alertar sobre a necessidade e a tarefa antess que a mesma fique pronta para submeter, este controle já existe e exige ambos ao tentar submeter, a propósito. 
- [x] Adicionar um ícone de download com label Baixar ao lado do ícone de lupa, adicionar uma pequena distancia entre eles.
- [x] Ao lado de baixar, deve ter uma pequena lupa que abre um modal que ocupa 90% da tela afim de permitir boa manipulação do PDF e ainda comparar as informações das despesas,
    componete reutilizável composto de duas partes, à esquerda as informações da despesa e à direita o visualizado do PDF.
    - [x] Em visualizar comprovante "IDs de Referência \nServentia: 50\nCat: 1 / Sub: 1" Deve aparecer os nomes completos de Cat e Sub ao invés de ID
- [x] Iconizar o menu lateral
- [ ] Icones melhores/mais bonitos/coloridos no menu lateral
- [ ] Diferenciar os ícones de 'Admin' e 'Solicitações de Categoria'
- [x] Em 'Buscar por ID' em /admin após clicar em 'Categorias', no formulário de busca, o botão 'Buscar' está desproporcional e grende
- [x] Em 'Buscar por ID' em /admin após clicar em 'Categorias', no formulário de busca, ao invés de usar 'ID', deve usar nome da Categoria ou Subcategoria num input que case parcialmente a partir da segunda letra
   - [x] Assim a tabela nesta tela deve ser atualizada conforme a busca parcial é executada
   - [x] O componente que mostra o texto 'Encontrado' não é mais necessário
   - [x] A mesma deve ficar mais abaixo próxima da tabela categoria
   - [?] O filtro deve ter a capacidade de ignorar acentos e ç
- [x] Em "Nova subcategoria" o input 'Categoria pai (ID)' deve ser uma seleção com as categorias já registradas
- [x] Em /despesas, o botão 'Submeter' deve aparecer depis do botão 'Detalhes' não está seguindo o padrão de cores para estatus, corrigir
- [x] No menu lateral não deve aparecer "Com Pendência" Para quem é do cartório, a rota /despesas/pendentes não deve ser permitida, inclusive
- [x] Em /despesas, o filtro 'Tipo de cartorio' para quem é do cartório não está funcionando . O filtro período também está falhando. Só STATUS está ok. Para cogex_auditor está ok e assim deve ficar, não mude isso.
- [x] Em /despesas para o estatus "PENDENTE DE ESCLARECIMENTO" aparece o botão responder que abre um modal que deve mostrar o questionamento enviado pelo auditor para leitura
   - [x] Em /despesas/xx deve aparecer também o questionamento enviado pelo auditor para leitura e o botão responder para abrir o modal de resposta também, ambos devem aparecer abaixo do conteúdo existente.
- [x] Em /despesas/xx O segundo container, 'Comprovantes' precisa ser mais robusto, podendo visualizar o documento, remover e adicionar outro outro documento.
   - [x] Nesse sentido, realizar upload deve ficar desbloqueado após os dois tipos de documentos terem sido enviados, desbloquea se pelo menos um for apagado. Adicionar um X à tabela no fim de cada linha para para retirar um documento
- [x] Em menu, subistitua 'Comprovantes' por 'Documentos'
   - [x] Faça o mesmo no container 'Comprovantes' em /despesas/xx
   - [x] /comprovantes deve mudar também, deve se tornar /documentos
- [x] Aplicar devdocs/cogex.png ao topo do menu, para todos os usuários no lugar de um pequeno quadrado atual, ao lado de 'Exofi Despesas'
   - [x] Substitua 'Exofi Despesas' por 'Despesas' apenas
- [x] /comprovantes deve mostrar apenas os da serventia atual para quem não é da cogex, no momento está mostrando todos
- [x] Em /despesas a tabela deve mostrar Categoria e Subcategoria antes de Descrição
- [ ] Responder Pendente não deve ser aceito sem "Resposta", Vazio/Espaços e outros do tipo não valem
- [x] Ampliar o caontainer para ocupar mais espaço lateral na tela
- [x] A tabela deve aparecerzebrada e responder ao mouse
- [ ] Em 'Questionamentos do Auditor' de '/despesas/89' 'Sua Resposta:' deve aparecer indentada na solicitação a qual pertence
- [ ] Adicionar Gráficos
- [ ] Em /relatorios, 'Resumo' deve mostrar a estatistica de todas as entradas
- [ ] Para consistência, Entradas: xx e Valor Total:R$ xx, deve aparecer também em 'Resumo' é para todas as entradas
- [ ] Em /relatorios, 'Resumo' deve mostrar a estatistica de paginação atual logo acima da tabela com 'Resumo desta tela' de forma discreta
- [ ] Desabilitar 'Documentos' em menu para a serventia
- [ ] O filtros de STATUS estão com estilos inconsistentes conforme cliques variados

## Auditor

- [x] Ver categorias solicitadas em um menu lateral para quem é auditor
   - [ ] Aprimorar
- [x] Para auditor, em /despesas, retirar o botão 'Esclarecimento'
- [x] Para auditor, em /despesas, ver o botão 'Marcar como Pendente' não estã seguindo o padrão de cores para estatus, corrigir
- [x] A despesa 89 teve pedido "PENDENTE DE ESCLARECIMENTO" e foi esclarecido e ficou com STATUS SUBMETIDA, mas não apareceu novamente em Despesas; para o auditor, só Relatórios aparece corretamente com status também correto de SUBMETIDA.
   - [x] Deve continuar mostrando em ordem de ID, pois do jeito que está ela foi pro fim da paginação.
- [x] Uma entrada no menu, onde mostra acompanhar com pendencias que aparecem. Label: "Com Pendencias"
   - [x] Mesmo as que já estão com outros STATUS devem aparecer lá, pois são as que deram alguma necessidade de atenção e por isso é importante estarem ali com um acompanhamento mais de perto.
- [x] Não está abrindo o modal para indicar o motivo da pendência em Relatórios deve ser adicionado em despesas o componente ser reutilizável em /despesas e em /despesas/pendentes
   - [x] Não pode ser possível marcar como 'Pendente' sem sem pôr motivo, pois não faz sentido
   - [x] Em despesas/pendentes, retirar a coluna ACOES
      - [x] O mesmo em /relatorios
- [x] Um sistema de filtro baseado nos mesmos existentes em Relatórios deve ser adicionado em despesas o componente ser reutilizável em /despesas e em /despesas/pendentes
- [x] Para auditor, em /relatorios, a coluna serventia está mostrando além das 22 primeiras na tabela, corrigir
- [ ] __Para auditor, em /despesas, não está aparecendo dados apesar de já estar aparecendo os filtros__
- [x] Em /admin, ao clicar em 'Categorias' o botaão excluir falha.

### Filtros

- [@] Visualizar as despesas em lista por dois filtros, inicialmente por mês atual por padrão, e o segundo por status SUBMETIDA; paginação padrão de 50 itens 
    - [x] Assim decorre que esse filtro fique salvo até que nova combinação seja feita e passe a valer até que o usuário troque novamente
- [x] Em /relatorios as informações da tabela dos status deve ter os 'status+"seu total"' em um elemento e seguindo a cor já usada na lista despesas. Tais elementos deve ficar em um elemento na parte superior do dashboard, log abaixo da navbar.
     - Assim, todo o espaço deixa de estar dividido em duas colunas "Relatorios" e "Auditoria de despesas", ficando apenas a última com seus elementos internos distribuídos em linha.
- [x] Onde está 'Relatorios' deve ficar 'Resumo' e este deve ser dinânmico e acompanhar o filtro
- [x] Onde se filtra por mês está sendo usado número 1 até 12, deve aparecer o nome do mês com a primeira letra maiúscula
- [x] Onde se filtra por ano está sendo usado um componente incremental e deve ser usado um calendário para que mostra os anos
- [x] Unir aos componentes de seleção de mês e ano em um calendário que mostra ambos apenas, sem os dias
- [x] Em /relatorios, na mesma linha onde fica o botão 'Aplicar' e 'Limpar', mas à direita, deve aparece o total de entradas que o filtro retornou, e o total o clicar em 'Limpar'
- [x] Em /relatorios, na tabela a coluna "Serventia" Está mostrando ID, deve mostrar Label ou Nome
- [x] Em /relatorios, antes da coluna Descrição, deve aparcer Categoria e depois Subcategoria
- [x] Em /relatorios, na lista de seleção Serventia, deve aparecer somente as 22 primeiras e Todos
- [x] Em /relatorios, na lista de seleção 'Tipo de cartorio' as 5 primeiras e Todos
- [x] Em /relatorios, 'Auditoria de despesas' a seleção de 'Período' está larga demais, deve ficar do tamanho das outras
- [x] Em /relatorios, um filtro de 'Status' deve estar disponível ao lado de 'Período'
- [x] Em /relatorios, 'Auditoria de despesas' ao lado de 'Entradas' deve aparecer o total da soma da coluna 'Valor' considerando todos os filtros ativos, talvez seja necessário um novo endpoint na API para dar suporte, ambos devem ter o valor alinhados a direita
- [x] Filtro imediato para os STATUS em botoês com Label dos tipos possíveis, 'PENDENTE DE ESCLARECIMENTO' deve ficar apenas PENDENTE e as cores deve seguir o padrão já em uso. Pode ficar após o Botão 'Limpar' com um divisor vertical. Assim 'Total de entradas: XX' poderia subir e ficar no lugar do componete que mostra o Status e sua caixa de seleção.
   - [x] Houve regressão em "- [x] Filtro imediato para os STATUS em botoês com Label dos tipos possíveis, 'PENDENTE DE ESCLARECIMENTO' deve ficar apenas PENDENTE e as cores deve seguir o padrão já em uso. Pode ficar após o Botão 'Limpar' com um divisor vertical. Assim 'Total de entradas: XX' poderia subir e ficar no lugar do componete que mostra o Status e sua caixa de seleção." Em /relatorios , para auditor isso deve continuar como estava. EM algum momento recente você retirou. Retorne como antes, pois era de melhor usabilidade.
   - [x] Aumentar o destaque do botão de filtro ativado para o Status
   - [x] Somente o botão de filtro ficou bom o destaque e sua borda está maior que as outras quando não está selecionado. Unificar os destaques
- [x] Somente das 22 primeiras Serventias deve ser mostradas
- [x] Em /relatorios, 'Entradas' e 'Valor Total' deve estar separados um abaixo do outro
- [x] __Em /relatorios, filtro por 'Período' não está funcionando__ Está ok. É que as amostras são todas de 2025, na carga automática 
- [x] Agora que há filtros para o STATUS, o componente em /dashboard pode ter um link para relatório o filtro de status aplicado, respeitando os outros filtros já salvos
   - [x] O mesmo deve ser ajustado em /admin
   - [x] Mas os cards não estão respeitando o padrão de cores para os STATUS, ajustar conforme
- [ ] Toda vez que um 'select' de filtro diferente do inicial está ativado, uma cor de destaque para o fundo do select
- [ ] A despesa deve ter um contador que incrementa a cada vez que o auditor a pôe como pendente, de tal forma que será possível rastrear as que foram demasiadas problemáticas @feature
   - [ ] Isso implica novas telas para suporte, avaliar quais seriam e criá-las
- [x] Ao clicar em 'Documentos', no menu lateral, para 'Auditor' é preciso retirar as 'Ações' Editar e Excluir
   - [x] Adicionar 'Detalhes' no lugar
   - [x] Avaliar no backend, como está a permissão para 'Editar' e 'Excluir', que só pode ser feita via suporte por cogex_admin, com documentação específica @suporte
- [@] Em /documentos, para Auditor e Admin
   - [x] Retirar os caontainers 'Upload' e 'Criar via JSON'
   - [x] Garantir que Auditor e Admin não possam criar documentos via 'Upload' e 'Criar via JSON', mesmo diretamente por API @security @DDD
   - [x] Bloquear upload e create quando a despesa não for da serventia do usuário (validação extra no service) @DDD
   - [x] Em /documentos, baixa o PDF, mas não visualiza ao clicar na 'Lupa'. Retornou isso: {"path":"/api/documentos/files/29c37617-1ee1-4a8c-86d1-1569304d78e1_comprovante_pagamento.pdf","error":"Unauthorized","message":"Nao autenticado","errors":{},"timestamp":"2026-02-12T15:42:35.534993550Z","status":401} 
   - [x] Em /documentos, Adicionar o nome da Serventia do documento na tabela, se o usuário for da COGEX
   - [x] Em /documentos, Adicionar limite de paginação. Incluir padrão de 50 itens
   - [x] Em /documentos, Desabilitar o link nos nomes dos arquivos e adicionar antes dos nomes e adicionar os mesmos ícones de Download e Visualização que aparecem em /despesas
- [ ] Informar tamanho do arquivo
- [ ] Data de upload do arquivo deve ser automática no banco de dados

## Security

- [ ] Checar validação de todas interações (elementos obrigatório e entradas de informação/segurança da informação)
- [ ] Acesso externo em http://10.1.20.196:3001

## Caraga inicial

- [x] Criar uma variação de 3 a 6 tipos de despesas com status automáticos variados para os primeiros 22 registros da tabela de serventia_extrajudicial. Faça isso em src/main/resources/data.sql de preferencia por script
- [x] Funcionou, mas não ficou muito legal, pois como a entrada foi feita direto no banco sem levar em consideração regras de negócio como a necessidade de ter arquivo pdf de 'Nota Fiscal' e 'Comprovante de pagamento' antes de poder ter o status de submetida. Avalie o arquivo de testes .py e gere estas entradas corretamente, conforme ocorre por esse arquiv. 
    - [x] O PDF ficou pontual. Mas deve ser de tamanho A4 com as informações detalhadas da mesma (Serventia, Competência, Categoria, Subcategoria, Descrição, Valor), cada informação por linha. Ajuste populate_data.py


## Dev

- [ ] Teste automatizados de UI por User Estories
- [ ] Fazer essa padronização ajustando o SecurityConfig para usar o mesmo esquema do RestExceptionHandler (incluindo timestamp e errors quando aplicável).

## Preset

-[x] popular as tabelas `Categoria` e `Subcategoria` do nosso sistema (via `data.sql`), para garantir a padronização.


### Commands

- [ ] .`.venv/bin/pytest devdocs/despesa-api-mvp.py -v` ou `./.venv/bin/pytest devdocs/despesa-api-mvp.py -v`
- [ ] python3 devdocs/populate_data.py
- [ ] sleep 10 && curl -u cogex_admin:password http://localhost:8080/api/relatorios/despesas/estatisticas
Avalie o significado no sistema para os tipos de STATUS, principalmente pendente

## Solicitado 02/09

### Ambos

- [x] Uma lista de Categorias numa coluna e em outra suas subcategorias. Enquanto listas as subcategorias, da mesma categoria, apenas a primeira linha deve aprecer com o nome da categoria, as demais em branco.
- [x] Entender melhor a questão de como deve ser o número de documentos necessários para o titular submeter
   - São dois mesmo que podem ter vários nomes para o que hoje está como NT_Fiscal e a partir de agora serão chamados de 'Documento Financeiro'
   - [x] A nomenclatura correta para esses arquivos. Será 'Documento Financeiro'
- [x] Como funciona o processo de novos colaboradores? Qual a melhor forma de integrar com esse sistemas quanto a adimissão/demissão? Delegatário é o Responsável ou a COGEX?
   - Passa pela COGEX, mas não integrará o sistema. Disso tirou-se apenas que caberá ao Delegatário adicionar e removar o acesso aos seus colaboradores. O sistema considera que todos os trâmites na COGEX já foram realizados e é permitido ao Delegatário adicionar o colaborador. Sendo sua única e exclusiva responsabilidade por isso.
   - [ ] Implementar essa Gerência de Usuários das Serventias

### Dra

- [ ] Encontrar maneira de não permitir que os valores sobre o qual o delegatário presta contas venha de Associação ou Cooperativa
   - Sugestão: Usar obrigatoriamente BB ou Caixa (De acordo com análise prévia) Isso também permite uma forma de conectar valores pagos com recebido, veja na análise
   - Carol irá ver essa possibilidade com as Serventias

### Carol

- [x] /relatorios deve ser adaptado para aparecer para quem não é da COGEX, mas deve poder ver apenas informações da serventia a qual pertence o usuário.
- [x] Datas da 'Competencia das despesas' deve aparecer nas tabelas
- [ ] Ajustar o resumo/estatísticas para usar o endpoint de /api/relatorios (caso queira estatísticas globais mesmo para cartório).
- [ ] Esconder filtros que não façam sentido para serventia (ex.: tipo de cartório).
- [ ] Pagamento em dinheiro só tem um recibo, o qual seria o único documento, criar uma forma de adaptar a esta realidade.
   - Há uma msg no zap com proposta de estabelecer um limite, será discutido com as COGEX mais adiante

### Alcione

- [ ] Algum modo de adicionar a despesa como aprovada, mas com glosa => Coluna com valor aprovado
   - Após Reunião com Carol, informei minha ideia de como implementar isso no fluxo já existentes como 'Pendencia'. Onde o Delegatário deve contabilizar corretamente e adicionar a diferença entre o valor pago e o valor próprio.
   - Assim fica destacado o valor que foi pago, mas também separado para contabilidade o valor devido a ser aprovado. É responsabilidade do delegatario a prestação de contas correta. Uma vez passado o prazo de pagamento, pode haver cobrança de adicional e o comprovante era enviado com o valor atualizado, mas só cabe o aceite ao valor inicial. Isso gera necessidade de conferência em cada nota para ver se isso não ocrreu. Não havia uma forma de controlar essa especificação de forma granular e deixar a responsabilidade de informar a quem cabe. Tal situação gera maior carga cognitiva para todas as notas, o que será evitado conforme tais ocorrencias @feature @conceito
   - [ ] Valor, Em 'Nova Despesa', agora 'Valor no Vencimento' + 'Multas + Juros'
      - [ ] Não informar 'Multas + Juros' impede o cadastro de 'Nova Despesa' com modal informativo
   - [ ] Tal informação deve ficar no formulário de 'Nova Despesa'
   - [ ] Um relatório ou visualização desse total de glosa, Valor Total sem Glosas, decorre naturalmente do novo campo

### Márcio

- [ ] Voltar em alguns momentos, ex: após clicar em detalhes
 
### Dev

- [x] Em admin -> Categorias, 'Editar' deve lançar uma modal
- [x] Em admin -> Categorias, 'Excluir' está abrindo a menssagem em alert() do navegador e deve ser modal com retirada da entrada da tabela, mas sem mover a janela pro início nem scroll, deve ser suave a retirada 
- [x] Em admin -> Categorias, ao lado de 'Categorias' deve aparecer 'Categorias Aninhadas', deveria estar ao lado dos 3 botões superiores e com página exclusiva
   - [x] Uma lista de Categorias numa coluna e em outra suas subcategorias. Enquanto listas as subcategorias, da mesma categoria, apenas a primeira linha deve aprecer com o nome da categoria, as demais em branco.
   - [x] Deve haver um botão que para exibir só as categorias e outro para todas. Para esses botões, use o mesmo padrão do STATUS em /relatorios
   - [x] O filtro 'Filtrar por nome (Categoria ou Subcategoria)' deve funcionar aqui também. Assim há duas experiencias de visualização.
- [ ] Em devdocs/populate_data.py, aprimorar para variar os 'Tipo de cartorio', pois no momento está sendo feito apenas para 'Registro de imóveis'
   - [ ] Adicionar o dados para os anos de 2025 e 2026, até o dia atual da execução do script
   - [ ] O Script não deve adicionar 'Tipos de cartorio' além dos 5 que já existem como inicias
   - [ ] O Script não deve adicionar 'Serventias' além dos 22 que já existem como inicias
   - [ ] 'Regras de despesa' deve ser apenas sobre as 'Serventias' além dos 22 que já existem como inicias
- [ ] Em /admin/serventias, os containers devem ocupar todo espaço disponível, pois há e estão se sobrepondo
- [ ] Em /admin/usuarios, os containers devem ocupar todo espaço disponível, pois há e estão se sobrepondo

"Se quiser, posso também garantir que NF e Comprovante sejam obrigatórios antes do envio da despesa (validação já existe no fluxo, mas posso reforçar no backend)"
Não está lá? Verifique, nenhuma validação pode ser só no frontend. Primeiro sempre no backend

### Questões pra estudo

- [x] Em 'Categorias Aninhadas', Como seria o SQL para produzir a mesma tabela?
   - Crie um tutorial abaixo sobre os conceitos necessários para entender a query de forma natural. Seja bem didático, proponha queries intermediárias como exemplo e o que mais achar necessário para alcançar o objetivo. Realce os níveis de conhecimento para cada parte (básico, médio e avançado) Use emojis
- [ ] Seria uma melhor forma de tratar o delete de uma categoria, considerando caso já exista despesas anotadas com ela, o que fazer? COmo impacta em todo o sistema e possíveis gráficos? E da tela de Categorias, como deveria aparecer conforme opções acima?


