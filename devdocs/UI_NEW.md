# UI_NEW.md

Objetivo
Instruir uma IA a ajustar a interface web existente (despesas-front-mvp) para cobrir "Atual para aprimoramento I" sem criar um design novo. Reaproveitar classes e componentes atuais (surface, form-grid, table, btn, helper, inline-actions, pill).

Contexto tecnico
- App Next.js em `despesas-front-mvp`.
- AuthContext ja exposto via `useAuth()` (token, role, logout).
- Navegacao em `components/AppShell.tsx` e telas em `app/*`.

Principios
- Nao quebrar fluxos atuais.
- Restringir recursos por role (RBAC) e esconder itens sem permissao.
- Preferir novos componentes simples ao estilo atual (sem bibliotecas novas).
- Persistir filtros no localStorage e aplicar somente via botao "Aplicar".

Novidades a incorporar (UI)

1) Gestao de Serventias (apenas RULE_COGEX_ADMIN)
- Criar tela de "Serventias" ou nova aba no AdminDashboard.
- Funcionalidades:
  - Listar serventias com busca simples (nome/descricao) e badge de status.
  - Criar/editar serventia (nome, codigo, delegatario).
  - Detalhe de serventia com historico de Tipos de Cartorio.
  - Vincular/encerrar TIPO_DE_CARTORIO com datas de inicio/fim e autor exibido.
- UI recomendada:
  - Lista em tabela (`table`), botoes `btn--secondary`/`btn--ghost`.
  - Formulario em `surface--muted` com `form-grid`.

2) Gestao de Tipos de Cartorio (apenas RULE_COGEX_ADMIN)
- Permitir visualizar lista de tipos.
- Criar novo tipo (se permitido) e listar ativos/inativos.
- Nao permitir delete fisico na UI, apenas encerrar (status inativo).

3) Delegatario
- Exibir e editar o delegatario no detalhe da serventia.
- Mostre informacao atual e ultima alteracao, se vier do backend.

4) Cadastro de usuarios e perfis de dominio (COGEX_ADMIN)
- Criar tela/aba "Usuarios" com:
  - Lista de usuarios por serventia.
  - Form de criacao com: nome, email, serventia, RULE_CARTORIO_*.
  - Opcao para vincular/alterar serventia.
- Deixar claro o nivel de permissao (ex.: "Apoio (5)").

5) Auditoria com filtros persistentes
- Definir local de auditoria:
  - Preferencia: pagina `app/relatorios/page.tsx`.
  - Alternativa: nova pagina `app/auditoria/page.tsx`.
- Adicionar barra de filtros:
  - ServentiaExtrajudicial (select).
  - Tipo de Cartorio (select dependente da serventia).
  - Mes/Ano (selects ou input tipo mes).
  - Botao "Aplicar" e botao "Limpar".
- Persistencia:
  - Salvar ultimo estado em localStorage com chave unica (ex.: `auditFilters`).
  - Ao carregar pagina, ler cache e aplicar no UI.
  - So refazer fetch quando clicar "Aplicar".

6) Regras de permissao no UI
- Mapear roles:
  - RULE_COGEX_ADMIN: acesso total aos cadastros e auditoria.
  - RULE_CARTORIO_TITULAR=1, INTERINO=2, SUBSTITUTO=3, APOIO=5.
- Ajustar exibicao de botoes/acoes:
  - "Lancar despesas": visivel para >= APOIO.
  - "Aprovar edicao": visivel para >= APOIO.
  - "Enviar para COGEX": visivel apenas para <= SUBSTITUTO (3).

Implementacao sugerida
- Criar componentes novos em `despesas-front-mvp/components/`:
  - `GerenciarServentias.tsx`
  - `GerenciarTiposCartorio.tsx`
  - `GerenciarUsuarios.tsx`
  - `AuditoriaFiltros.tsx`
- Integrar no `AdminDashboard` com nova(s) aba(s) e no menu lateral.
- Atualizar `services/api.ts` com funcoes stub (ou reais) para:
  - listar/criar/editar serventias
  - listar/criar/encerrar tipos de cartorio
  - vincular tipo a serventia com inicio/fim
  - listar/criar usuarios
  - obter dados para auditoria com filtros

Criterios de aceite (UI)
- Itens do menu so aparecem para usuarios autorizados.
- Filtros ficam visiveis e persistem entre navegacoes.
- Fluxos de cadastro possuem feedback (helper success/error).
- Nao ha remocao fisica no UI (usar "encerrar"/"inativar").
- Estilo visual segue padrao atual.

Observacoes
- Se o backend nao estiver pronto, usar mocks locais com dados coerentes.
- Evitar novas dependencias; priorizar o que ja existe.
