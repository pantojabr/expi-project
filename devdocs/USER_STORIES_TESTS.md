# USER_STORIES_TESTS.md

Objetivo
Guia de testes manuais baseado nas user stories por RULE, alinhado aos fluxos e endpoints testados em `devdocs/despesa-api-mvp.py`.

Pre-requisitos gerais
- API e front em execucao.
- Usuarios validos: cogex_admin, cogex_auditor, titular, interino, substituto, apoio.
- Base com pelo menos 2 serventias, 2 tipos e algumas despesas.
- Pastas de uploads configuradas.

Convencoes
- Cada teste referencia a User Story.
- Sempre registrar: usuario, data/hora, ambiente e evidencias (prints/IDs).

## Bloco A - COGEX_ADMIN

T-ADM-01 - Gerenciar Serventias (US-ADM-01)
- Login: cogex_admin
- Passos:
  1) Acesse Menu > Serventias.
  2) Crie uma nova serventia com nome/codigo/delegatario.
  3) Edite a serventia e salve.
- Esperado:
  - Serventia aparece na tabela.
  - Alteracoes persistem.

T-ADM-02 - Importar Serventias (US-ADM-02)
- Login: cogex_admin
- Passos:
  1) Em Serventias, cole 3 linhas no bloco "Importar serventias".
  2) Clique "Importar lista".
- Esperado:
  - Serventias aparecem na lista sem erro.

T-ADM-03 - Gerenciar Tipos (US-ADM-03)
- Login: cogex_admin
- Passos:
  1) Acesse Menu > Tipos de cartorio.
  2) Crie um novo tipo.
  3) Edite o tipo.
  4) Inative o tipo.
- Esperado:
  - Tipo criado/alterado.
  - Inativado marcado como inativo.

T-ADM-04 - Importar Tipos (US-ADM-04)
- Login: cogex_admin
- Passos:
  1) Em Tipos, cole 3 linhas no bloco "Importar tipos".
  2) Clique "Importar lista".
- Esperado:
  - Tipos aparecem na lista.

T-ADM-05 - Vincular Tipo com PDF (US-ADM-05)
- Login: cogex_admin
- Passos:
  1) Em Serventias, selecione uma serventia.
  2) Preencha tipo, aplicadoPor, motivo e anexe PDF.
  3) Clique "Vincular tipo".
- Esperado:
  - Historico mostra novo vinculo com status ativo.
  - Motivo exibido.

T-ADM-06 - Encerrar Vinculo com PDF (US-ADM-06)
- Login: cogex_admin
- Passos:
  1) Em Serventias, selecione a serventia com vinculo ativo.
  2) Preencha encerradoPor, motivo e PDF.
  3) Clique "Encerrar tipo".
- Esperado:
  - Vinculo marcado como encerrado.
  - Motivo de encerramento exibido.

T-ADM-07 - Baixar Comprovantes (US-ADM-07)
- Login: cogex_admin
- Passos:
  1) No historico de tipos, clique "Aplicacao".
  2) Clique "Encerramento".
- Esperado:
  - PDFs baixados com sucesso.

T-ADM-08 - Gerenciar Usuarios (US-ADM-08)
- Login: cogex_admin
- Passos:
  1) Acesse Menu > Usuarios.
  2) Crie usuario com nome, email, role e serventia.
  3) Edite o usuario.
- Esperado:
  - Usuario aparece na lista com perfil correto.

T-ADM-09 - Categorias/Subcategorias (US-ADM-09)
- Login: cogex_admin
- Passos:
  1) Menu > Categorias.
  2) Criar categoria e subcategoria.
  3) Editar e remover (se permitido).
- Esperado:
  - CRUD funciona conforme permissao.

T-ADM-10 - Regras de Despesa (US-ADM-10)
- Login: cogex_admin
- Passos:
  1) Menu > Regras de despesa.
  2) Criar regra com categoria/subcategoria, motivo e (opcional) serventia.
- Esperado:
  - Regra aparece na tabela.

T-ADM-11 - Estatisticas e Exportacao (US-ADM-11)
- Login: cogex_admin
- Passos:
  1) Menu > Relatorios.
  2) Visualizar estatisticas por status.
  3) Menu > Exportacao e baixar XLSX.
- Esperado:
  - Estatisticas exibidas.
  - Download concluido.

## Bloco B - COGEX_AUDITOR

T-AUD-01 - Lista Auditoria (US-AUD-01)
- Login: cogex_auditor
- Passos:
  1) Menu > Relatorios.
  2) Ver tabela de auditoria.
- Esperado:
  - Despesas listadas.

T-AUD-02 - Filtros Auditoria (US-AUD-02)
- Login: cogex_auditor
- Passos:
  1) Escolha serventia, tipo, mes e ano.
  2) Clique "Aplicar".
  3) Navegue para outra pagina e retorne.
- Esperado:
  - Filtros persistem.
  - Resultados so mudam após aplicar.

T-AUD-03 - Workflow Auditoria (US-AUD-03)
- Login: cogex_auditor
- Passos:
  1) Menu > Despesas.
  2) Em uma despesa SUBMETIDA, clique Aprovar.
  3) Em outra, clique Rejeitar.
  4) Solicite esclarecimento.
- Esperado:
  - Status muda conforme acao.
  - Esclarecimento cria solicitacao.

T-AUD-04 - Detalhe/Comprovantes (US-AUD-04)
- Login: cogex_auditor
- Passos:
  1) Acesse detalhe de uma despesa.
  2) Abra comprovantes anexados.
- Esperado:
  - Visualizacao correta.

## Bloco C - Serventia (Titular/Interino/Substituto/Apoio)

T-SER-01 - Registrar Despesa (US-SER-01)
- Login: apoio
- Passos:
  1) Menu > Nova despesa.
  2) Preencha dados e anexe comprovante.
- Esperado:
  - Despesa criada com status REGISTRADA.

T-SER-02 - Submeter (US-SER-02)
- Login: substituto (ou titular/interino)
- Passos:
  1) Menu > Despesas.
  2) Em despesa REGISTRADA, clique "Submeter".
- Esperado:
  - Status muda para SUBMETIDA.

T-SER-03 - Editar Despesa (US-SER-03)
- Login: apoio
- Passos:
  1) Abra detalhe de despesa REGISTRADA.
  2) Edite campos e salve.
- Esperado:
  - Alteracoes persistem.

T-SER-04 - Responder Esclarecimento (US-SER-04)
- Login: apoio (ou outro da serventia)
- Passos:
  1) Em despesa PENDENTE_DE_ESCLARECIMENTO, clique "Responder".
  2) Informe ID da solicitacao e resposta.
- Esperado:
  - Solicitacao marcada como respondida.
  - Despesa retorna para SUBMETIDA.

T-SER-05 - Solicitar Categoria (US-SER-05)
- Login: titular
- Passos:
  1) Clique "Sugerir categoria".
  2) Preencha tipo, justificativa e (se subcategoria) categoria pai.
- Esperado:
  - Solicitação enviada com status pendente.

## Bloco D - RBAC e Seguranca

T-RBAC-01 - Rotas Restritas (US-RBAC-01)
- Login: titular
- Passos:
  1) Tentar acessar /admin/serventias, /admin/usuarios.
- Esperado:
  - Acesso negado/redirecionado.

T-RBAC-02 - Lancar Despesa (US-RBAC-02)
- Login: apoio (permitido) e substituto (bloqueado para editar)
- Passos:
  1) Tentar criar despesa com substituto.
  2) Tentar criar despesa com apoio.
- Esperado:
  - Somente apoio (>=5) pode criar.

T-RBAC-03 - Enviar para COGEX (US-RBAC-02)
- Login: apoio e substituto
- Passos:
  1) Em despesa REGISTRADA, tentar submeter com apoio.
  2) Repetir com substituto.
- Esperado:
  - Apoio nao ve/nao consegue submeter.
  - Substituto consegue.

Evidencias
- Para cada teste, salvar: prints, ID de entidades e timestamp.

