# USER_STORIES.md

Objetivo
Documentar as user stories principais do dominio de despesas, organizadas por RULE (perfil) e alinhadas aos fluxos testados em `devdocs/despesa-api-mvp.py`.

Convencoes
- RULEs (perfil/role):
  - COGEX_ADMIN (administracao)
  - COGEX_AUDITOR (auditoria)
  - CARTORIO_TITULAR (1)
  - CARTORIO_INTERINO (2)
  - CARTORIO_SUBSTITUTO (3)
  - CARTORIO_APOIO (5)

- Status de despesa: REGISTRADA, SUBMETIDA, APROVADA, REJEITADA, PENDENTE_DE_ESCLARECIMENTO
- Entidades chave: Serventia, Tipo de Cartorio, Usuario Dominio, Categoria/Subcategoria, Despesa, Comprovante, Regra de Despesa

## RULE_COGEX_ADMIN (Administracao)

US-ADM-01 - Gerenciar Serventias
Como COGEX_ADMIN, quero listar, criar e editar serventias, para manter o cadastro institucional atualizado.
- Criterios:
  - Posso criar/editar nome, codigo, delegatario e status.
  - Vejo serventias com status (ativa/inativa).
  - Acesso negado para outros perfis.

US-ADM-02 - Importar Serventias em lote
Como COGEX_ADMIN, quero importar uma lista de serventias por texto, para agilizar carga inicial.
- Criterios:
  - Cada linha gera uma serventia.
  - Linhas em branco sao ignoradas.
  - Sem falhas quando ja existir (idempotencia no backend).

US-ADM-03 - Gerenciar Tipos de Cartorio
Como COGEX_ADMIN, quero listar, criar, editar e inativar tipos de cartorio, para controlar as classificacoes oficiais.
- Criterios:
  - Inativacao nao remove fisicamente.
  - Tipos inativos aparecem como inativos.

US-ADM-04 - Importar Tipos de Cartorio em lote
Como COGEX_ADMIN, quero importar tipos por lista, para acelerar o cadastro.
- Criterios:
  - Cada linha gera um tipo.
  - Linhas em branco sao ignoradas.

US-ADM-05 - Vincular Tipo de Cartorio a Serventia
Como COGEX_ADMIN, quero vincular um tipo a uma serventia com comprovante PDF e motivo, para manter rastreabilidade e auditoria.
- Criterios:
  - Exige motivo e comprovante PDF valido.
  - Registra data de inicio e autor.
  - Gera historico consultavel.

US-ADM-06 - Encerrar Vinculo de Tipo de Cartorio
Como COGEX_ADMIN, quero encerrar o vinculo de tipo com motivo e comprovante PDF, para registrar fim do periodo e justificativa.
- Criterios:
  - Exige motivo e comprovante PDF valido.
  - Registra data de fim e autor.
  - Vinculo fica inativo, historico preservado.

US-ADM-07 - Baixar Comprovantes de Vinculo
Como COGEX_ADMIN, quero baixar comprovantes de aplicacao/encerramento, para auditoria documental.
- Criterios:
  - Posso baixar PDF de aplicacao e encerramento.
  - Erro 404 quando nao existir.

US-ADM-08 - Gerenciar Usuarios de Dominio
Como COGEX_ADMIN, quero criar e editar usuarios vinculados a serventia e RULE, para definir acesso e responsabilidades.
- Criterios:
  - Posso listar e atualizar usuarios.
  - Usuario possui nome, email, serventia e RULE.

US-ADM-09 - Gerenciar Categorias e Subcategorias
Como COGEX_ADMIN, quero CRUD de categorias e subcategorias, para garantir padronizacao.
- Criterios:
  - CRUD completo via UI.
  - Exclusao apenas quando permitido pelo backend.

US-ADM-10 - Gerenciar Regras de Despesa
Como COGEX_ADMIN, quero habilitar/desabilitar categorias/subcategorias por serventia com motivo, para controlar gastos permitidos.
- Criterios:
  - Requer motivo.
  - Pode ser global (sem serventia).

US-ADM-11 - Ver Estatisticas e Relatorios
Como COGEX_ADMIN, quero ver estatisticas por status e exportar planilha, para tomada de decisao.
- Criterios:
  - Dashboard com contagens por status.
  - Exportacao XLSX via endpoint.

## RULE_COGEX_AUDITOR (Auditoria)

US-AUD-01 - Listar Despesas para Auditoria
Como COGEX_AUDITOR, quero ver despesas submetidas, para analisar conformidade.
- Criterios:
  - Lista de despesas para auditoria.

US-AUD-02 - Filtrar Despesas por Serventia/Tipo/Mes/Ano
Como COGEX_AUDITOR, quero filtrar despesas por criterios, para focar analises.
- Criterios:
  - Filtros combinaveis (serventia, tipo, mes, ano).
  - Persistencia do filtro ate que eu clique em Aplicar.

US-AUD-03 - Aprovar, Rejeitar ou Solicitar Esclarecimento
Como COGEX_AUDITOR, quero aprovar/rejeitar ou solicitar esclarecimento, para concluir a analise.
- Criterios:
  - Acoes mudam status corretamente.
  - Solicitar esclarecimento cria solicitacao associada.

US-AUD-04 - Consultar Detalhe de Despesa
Como COGEX_AUDITOR, quero abrir o detalhe e seus comprovantes, para validar evidencias.
- Criterios:
  - Visualizo dados da despesa e comprovantes.

## RULE_CARTORIO_TITULAR / INTERINO / SUBSTITUTO / APOIO (Serventia)

US-SER-01 - Registrar Despesa
Como usuario da serventia, quero registrar uma despesa com categoria/subcategoria e comprovante, para iniciar o fluxo de auditoria.
- Criterios:
  - Status inicial REGISTRADA.
  - Comprovante anexado via upload.

US-SER-02 - Submeter para COGEX
Como usuario da serventia (nivel <= 3), quero submeter despesas registradas, para enviar para auditoria.
- Criterios:
  - Apenas RULE_CARTORIO_TITULAR/INTERINO/SUBSTITUTO podem submeter.

US-SER-03 - Editar Despesa Registrada
Como usuario da serventia (nivel >= 5), quero editar despesas registradas, para corrigir informacoes.
- Criterios:
  - Somente RULE_CARTORIO_APOIO (>=5) pode editar.

US-SER-04 - Responder Esclarecimento
Como usuario da serventia, quero responder solicitacoes de esclarecimento, para retomar analise.
- Criterios:
  - Resposta atualiza solicitacao e retorna despesa a SUBMETIDA.

US-SER-05 - Solicitar Nova Categoria/Subcategoria
Como usuario da serventia, quero solicitar criacao de categoria/subcategoria, para cobrir novos tipos de despesa.
- Criterios:
  - Envio contem tipo, justificativa e (se subcategoria) categoria pai.

## Seguranca e Acessos (RBAC)

US-RBAC-01 - Bloqueio de Rotas Restritas
Como sistema, quero bloquear acessos a rotas administrativas, para garantir seguranca.
- Criterios:
  - Nao logado ou sem permissao: acesso negado/redirecionado.

US-RBAC-02 - Acesso conforme RULE
Como sistema, quero aplicar permissoes por RULE, para manter governanca.
- Criterios:
  - Lancar despesas: >= APOIO.
  - Enviar para COGEX: <= SUBSTITUTO.
  - Aprovacao/edicao: >= APOIO.

