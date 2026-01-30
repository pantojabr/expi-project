# PRD_TESTES.md

Objetivo
Validar as entregas de "Atual para aprimoramento I" com foco em RBAC, cadastro de serventias e tipos de cartorio, delegatario, filtros de auditoria e regras de permissao. Este documento instrui uma IA/QA a executar testes funcionais e de aceitacao.

Escopo
- Cadastro de ServentiaExtrajudicial e TIPO_DE_CARTORIO (importacao e manutencao).
- Vinculo dinamico Serventia <-> TIPO_DE_CARTORIO com historico (inicio/fim e autor).
- Delegatario da serventia (admin COGEX).
- Filtros de auditoria por Serventia, TIPO_DE_CARTORIO e Mes/Ano, com persistencia.
- Cadastro de usuarios com perfil (RULEs) e dominio.
- Regras de permissao para lancar despesas, aprovar edicao e enviar para COGEX.

Fora de escopo
- Melhorias do "Atual para aprimoramento II/III".
- Alteracoes de design nao relacionadas aos fluxos acima.

Preparacao de dados (setup minimo)
- Serventias.txt: pelo menos 3 serventias distintas.
- Tipos_de_Cartorio.txt: pelo menos 3 tipos (ex.: Registro Civil, Tabelionato, Protesto).
- Usuarios de teste:
  - COGEX_ADMIN (ROLE/CLAIM correspondente).
  - CARTORIO_TITULAR (RULE_CARTORIO_TITULAR=1).
  - CARTORIO_INTERINO (RULE_CARTORIO_INTERINO=2).
  - CARTORIO_SUBSTITUTO (RULE_CARTORIO_SUBSTITUTO=3).
  - CARTORIO_APOIO (RULE_CARTORIO_APOIO=5).
- Pelo menos 5 despesas distribuidas em 2 serventias, meses diferentes e tipos de cartorio distintos.

Criterios de aceite (alto nivel)
- Apenas COGEX_ADMIN consegue criar/editar serventias, delegatarios e vinculos de tipo de cartorio.
- Vinculo de tipo de cartorio possui historico com inicio/fim e autor, sem exclusao fisica.
- Filtros de auditoria aplicam combinacoes Serventia, Tipo e Mes/Ano e persistem o ultimo estado.
- Regras de permissao operam por RULE_CARTORIO_* conforme definicao.

Casos de teste (prioritarios)

T001 - Acesso RBAC basico
- Dado usuario nao logado
- Quando acessa rotas admin/serventias/usuarios
- Entao recebe bloqueio/redirecionamento

T002 - COGEX_ADMIN cria serventia
- Dado usuario COGEX_ADMIN logado
- Quando cria serventia com dados validos
- Entao registro aparece na lista com createdAt/updatedAt

T003 - Importacao Serventias.txt
- Dado COGEX_ADMIN
- Quando executa importacao
- Entao todas as linhas criam entidades sem duplicidade

T004 - Importacao Tipos_de_Cartorio.txt
- Dado COGEX_ADMIN
- Quando executa importacao
- Entao tipos existem no cadastro com status ativo

T005 - Vinculo de tipo de cartorio (adicao)
- Dado COGEX_ADMIN
- Quando vincula tipo a uma serventia com data inicio
- Entao historico registra inicio, autor e status ativo

T006 - Vinculo de tipo de cartorio (remocao logica)
- Dado COGEX_ADMIN e vinculo ativo
- Quando remove o tipo
- Entao historico registra data fim, autor e vinculo fica inativo

T007 - Delegatario
- Dado COGEX_ADMIN
- Quando define delegatario
- Entao campo aparece na tela e API retorna no detalhe

T008 - Cadastro de usuario e dominio
- Dado COGEX_ADMIN
- Quando cria usuario com serventia e RULE_CARTORIO_*
- Entao usuario fica ativo e visivel na lista

T009 - Filtro auditoria default
- Dado usuario com permissao auditoria
- Quando acessa auditoria
- Entao Mes/Ano sao o mes/ano atual

T010 - Filtro auditoria combinando Serventia + Tipo + Mes/Ano
- Dado dados distribuidos
- Quando aplica filtros combinados
- Entao resultados correspondem ao recorte

T011 - Persistencia de filtros
- Dado filtros aplicados
- Quando navega para outra pagina e volta
- Entao filtros permanecem e resultados so mudam apos novo Apply

T012 - Permissao lancar despesas
- Dado usuario RULE_CARTORIO_APOIO ou superior
- Quando tenta criar despesa
- Entao permitido
- E usuarios abaixo disso sao bloqueados

T013 - Permissao aprovar edicao
- Dado usuario RULE_CARTORIO_APOIO ou superior
- Quando tenta aprovar edicao
- Entao permitido

T014 - Permissao enviar para COGEX
- Dado usuario RULE_CARTORIO_SUBSTITUTO (3) ou menor
- Quando tenta enviar para COGEX
- Entao permitido
- E usuarios com nivel maior (ex.: APOIO=5) sao bloqueados

Testes negativos
- Campos obrigatorios vazios em cadastro de serventia, tipo e usuario
- Tentativas de alteracao por usuario sem permissao
- Duplicidade de serventia/tipo

Evidencias
- Para cada teste: data/hora, usuario, ambiente, passos, prints de tela e resultado.

Notas
- Caso o backend nao esteja pronto, usar mocks coerentes e registrar a limitacao.
