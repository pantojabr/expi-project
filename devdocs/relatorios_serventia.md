# Relatorios para Serventia

## Problema observado
Ao acessar `/relatorios` como usuario de serventia, o front chama:

```
GET /api/auditoria/despesas?status=APROVADA&page=0&size=50
GET /api/auditoria/despesas/soma?status=APROVADA
```

E a API responde `403 Forbidden`, gerando na UI o erro "Failed to fetch auditoria despesas".

## Causa provavel do 403
O 403 normalmente indica que a rota ainda esta protegida por papel (ex.: apenas COGEX), ou que o backend nao foi reiniciado apos mudar `SecurityConfig`. Outra possibilidade e estar batendo em um backend diferente (ou sem auth correta).

## Objetivo
Permitir que usuarios de serventia vejam relatorios, mas **apenas das suas proprias despesas**, sem quebrar o modelo de seguranca.

## Alternativas robustas

### Opcao A (recomendada): manter `/api/auditoria/**` unica
- **Ideia:** Deixar o endpoint unico para todos os perfis autenticados.
- **Seguranca:** Quando o usuario e de cartorio, o backend ignora `serventiaId` do request e **forca** a serventia do usuario.
- **Vantagens:**
  - Nao duplica controllers ou servicos.
  - Mantem o front reutilizavel.
  - Centraliza a regra de seguranca no backend.

### Opcao B: endpoint dedicado para serventia
- Ex.: `/api/auditoria/serventia/despesas` e `/api/auditoria/serventia/despesas/soma`.
- **Vantagem:** isolamento explicito de rota.
- **Desvantagem:** duplicacao de controller/service e manutencao maior.

### Opcao C: validacao explicita na controller
- Se for cartorio e vier `serventiaId` diferente, retornar 403.
- Se vier vazio, forcar a serventia do usuario.
- **Vantagem:** nao duplica rotas.
- **Desvantagem:** espalha regra no controller.

### Opcao D: isolamento por tenant
- Aplicar tenantId no contexto de seguranca (Hibernate Filter / multi-tenant).
- **Vantagem:** robusto e automatico.
- **Desvantagem:** maior complexidade tecnica.

## Recomendacao
Seguir com a **Opcao A**. Ela equilibra seguranca e simplicidade, evita duplicacao e reduz risco de regressao.

## Checklist de diagnostico
- Reiniciar/rebuild do backend depois das mudancas em `SecurityConfig`.
- Verificar se o request esta autenticado (header presente).
- Garantir que o front aponta para o backend correto.

## Referencia tecnica
- Backend: `AuditoriaService.resolveServentiaId()` deve forcar a serventia quando o usuario for cartorio.
- Security: `/api/auditoria/**` deve estar `authenticated()` (nao restrito a COGEX).

## Possivel

  1. Adicionar um log em AuditoriaService para mostrar quem está chamando e qual serventia foi resolvida.
  2. Ajustar o frontend para esconder o filtro de "Serventia" quando for cartório (evita confusão).
  3. Criar uma rota dedicada se você preferir isolamento total.

## Exemplos de resposta

### 1) Lista paginada de despesas (Page<DespesaDTO>)
```json
{
  "content": [
    {
      "id": 123,
      "categoriaNome": "Material",
      "subcategoriaNome": "Papelaria",
      "descricao": "Compra de papel",
      "serventiaNome": "Cartorio X",
      "idServentia": "10",
      "statusAuditoria": "APROVADA",
      "valor": 250.5
    }
  ],
  "totalPages": 3,
  "totalElements": 101,
  "number": 0,
  "size": 50
}
```

### 2) Soma das despesas
```json
25000.75
```

## Cenarios de teste

### 1) Usuario de serventia
- **Quando** acessa `/api/auditoria/despesas`
- **Entao** so recebe despesas da sua serventia
- **E** o backend ignora `serventiaId` informado no request

### 2) Usuario de COGEX (admin/auditor)
- **Quando** acessa `/api/auditoria/despesas` sem `serventiaId`
- **Entao** recebe o conjunto conforme regra global de auditoria
- **Quando** informa `serventiaId`
- **Entao** o filtro e aplicado normalmente

### 3) Usuario nao autenticado
- **Quando** acessa `/api/auditoria/despesas`
- **Entao** recebe `401` com corpo padronizado

### 4) Usuario autenticado sem serventia vinculada
- **Quando** e perfil cartorio mas nao possui serventia
- **Entao** recebe lista vazia e soma igual a 0

## Checklist rapido com curl

> Substitua `<TOKEN>` e, se necessário, `<BASE_URL>`.

### 1) Listar despesas (paginado)
```bash
curl -fsS \
  -H "Authorization: Bearer <TOKEN>" \
  "<BASE_URL>/api/auditoria/despesas?status=APROVADA&page=0&size=50"
```

### 2) Somar despesas
```bash
curl -fsS \
  -H "Authorization: Bearer <TOKEN>" \
  "<BASE_URL>/api/auditoria/despesas/soma?status=APROVADA"
```

### 3) Forcar filtro de serventia (somente COGEX)
```bash
curl -fsS \
  -H "Authorization: Bearer <TOKEN>" \
  "<BASE_URL>/api/auditoria/despesas?serventiaId=10&status=APROVADA&page=0&size=50"
```

### 4) Checar resposta 401 (sem token)
```bash
curl -i \
  "<BASE_URL>/api/auditoria/despesas?status=APROVADA&page=0&size=50"
```
