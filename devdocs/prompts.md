src/main/java/br/jus/tjap/exofi/despesaapi/model/DominioRole.java está ROLE_CARTARIO_ZZ, onde na verdade deve ser ROLE_CARTORIO_ZZ ajuste lá e por onde for necessário inclusive nos testes e faltou  ROLE_COGEX_AUDITOR em src/main/java/br/jus/tjap/exofi/despesaapi/model/DominioRole.java e possíveis outros lugares e inclusive nos testes. Também estou vendo uma inconsistência nas STRINGS em src/main/java/br/jus/tjap/exofi/despesaapi/config/SecurityConfig.java com os nome em src/main/java/br/jus/tjap/exofi/despesaapi/model/DominioRole.java que deve orientar o uso geral pelo código para padronização. Avalie corrija.
"SERVENTIA", "ADMIN", "AUDITOR" ainda estão em SecurityConfig.java e devem ser substituidas por "ROLE_CARTORIO_TITULAR", "ROLE_COGEX_ADMIN" e "ROLE_COGEX_AUDITOR" e isso deve refletir em devdocs/despesa-api-mvp.py também. É importante manter essa consistência com src/main/java/br/jus/tjap/exofi/despesaapi/model/DominioRole.java apenas.
Cadastro de serventias por ROLE_COGEX_ADMIN
- Segurança por ROLE_COGEX_ADMIN: feito (despesa-api-mvp/src/main/java/br/jus/tjap/exofi/despesaapi/config/SecurityConfig.java)
- Lançar despesas >= ROLE_CARTORIO_APOIO: feito (POST/PUT despesa)
- Aprovar edição >= ROLE_CARTORIO_APOIO: não há endpoint específico
- Enviar para COGEX <= ROLE_CARTORIO_SUBSTITUTO: feito para submit (workflow/submeter)
- Permissão para “aprovar edição” já coberta via PUT /api/despesas/{id} com ROLE_CARTORIO_APOIO.
• Ajustei as verificações para garantir que somente ROLE_COGEX_ADMIN pode executar essas ações, e adicionei validação obrigatória de aplicadoPor/encerradoPor no service.
- ServentiaController: @PreAuthorize("hasRole('ROLE_COGEX_ADMIN')") em:
- TipoCartorioController: @PreAuthorize("hasRole('ROLE_COGEX_ADMIN')") em:
Se quiser, posso adicionar testes específicos garantindo 403 para qualquer role diferente de ROLE_COGEX_ADMIN nesses endpoints.
- Regras de acesso ampliadas (COGEX_ADMIN e ROLE_CARTARIO_*).
