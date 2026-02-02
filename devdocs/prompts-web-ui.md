TODO. Também restringi o cadastro de serventias/tipos para ROLE_COGEX_ADMIN. Não encontrei uma tela de auditoria no frontend para persistir estado de filtro; esse
- CRUD de serventia/tipo protegido por ROLE_COGEX_ADMIN.
As únicas ROLEs permitidas são as 'ROLE_CARTORIO_TITULAR', 'ROLE_CARTORIO_INTERINO', 'ROLE_CARTORIO_SUBSTITUTO', 'ROLE_CARTORIO_APOIO', 'ROLE_COGEX_ADMIN', 'ROLE_COGEX_AUDITOR';
SERVENTIA => ROLE_CARTORIO_APOIO
ADMIN => ROLE_COGEX_ADMIN'
AUDITOR => ROLE_COGEX_AUDITOR