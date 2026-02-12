# Regra de Acesso a Documentos (DDD)

## Objetivo
Definir, de forma consistente, **quem pode criar/editar/listar documentos** e **como o backend deve validar o acesso**. Esta regra foi escrita para ser **reutilizavel** em outros projetos e, ao final, traz a **customizacao do projeto atual**.

---

# Parte reutilizavel (generica)

## Conceitos por tras

### 1) Fonte da verdade no backend
Mesmo que o frontend esconda botoes, o **backend sempre valida** quem pode criar/alterar/ler. Isso evita bypass via chamadas diretas de API.

### 2) Escopo de acesso por dominio
Documento deve pertencer a um **agregado** (ex.: Despesa). Logo, permissao de documento depende da **permissao sobre o agregado**. Esse e o principio DDD de **consistencia do agregado**.

### 3) Autorizacao por papel + posse
Nao basta ter papel. O usuario precisa:
- **Papel valido** (ex.: cartorio pode criar)
- **Posse/escopo valido** (documento ligado a despesa da sua serventia)

### 4) Politica unificada
Regra uniforme para:
- `create`
- `update`
- `list by despesa`

Isso reduz riscos de brechas (ex.: bloquear update mas liberar listagem).

### 5) Erro padronizado
Respostas 401/403 devem seguir **formato unico** para simplificar o front e logs.

---

# Customizacao: projeto atual (despesa-api-mvp)

## Regras

### Criacao (POST)
- **Permitido apenas para perfis de cartorio**
- **Bloqueado para ADMIN/AUDITOR**

### Alteracao (substituicao do arquivo)
- **Somente por cartorio** e **apenas enquanto a despesa nao estiver APROVADA**
- A alteracao ocorre como **remover o documento atual e enviar outro**
- Requer validacao de serventia (despesa deve pertencer ao usuario)

### Edicao direta (PUT)
- **Nao permitido para nenhum perfil**

### Exclusao (DELETE)
- **Nao permitido para nenhum perfil**

### Listagem por despesa (GET /despesas/{id}/documentos)
- **Somente se a despesa pertencer a serventia do usuario** (quando usuario e cartorio)

### Listagem geral (GET /api/documentos)
- **Paginada** (page/size) com **padrao 50 itens**
- **Retorna `serventiaNome`** quando disponivel

## Onde esta aplicado
- Service: `DocumentoService.validateDespesaAccess(...)`
- Security: `SecurityConfig` com regras por metodo
- Erro padronizado: `RestExceptionHandler` + handlers de 401/403

---

# Como pedir isso desde o inicio (prompt)

Se a requisicao tivesse sido feita assim desde o comeco, o sistema ja teria nascido correto:

"Quero que o acesso a documentos siga regras DDD e seja validado no backend. 
- Cartorio pode **criar** documento apenas para despesas da sua serventia.
- Admin/Auditor **nao podem criar** documentos.
- Cartorio pode **substituir** documentos apenas enquanto a despesa nao estiver APROVADA (remove o atual e sobe outro).
- PUT e DELETE diretos nao devem existir (ou retornar 403/405).
- Listagem por despesa deve validar a serventia do usuario.
- Padronizar erros 401/403 no mesmo formato do resto da API.
Crie testes de seguranca cobrindo todos os papeis."
