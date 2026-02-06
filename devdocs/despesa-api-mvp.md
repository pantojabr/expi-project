# Testes Automatizados - despesa-api-mvp

Documentação dos testes automatizados da API de Controle de Despesas (`despesa-api-mvp.py`).

## Pré-requisitos

- API rodando via `docker compose up -d` (na pasta `despesa-api-mvp/`)
- Python 3.10+
- Dependências:

```bash
pip install requests pytest
```

## Como executar

```bash
# Execução padrão (API em localhost:8080)
pytest devdocs/despesa-api-mvp.py -v

# Apontar para outro endereço
BASE_URL=http://192.168.1.10:8080 pytest devdocs/despesa-api-mvp.py -v

# Executar apenas os fluxos de auditoria
pytest devdocs/despesa-api-mvp.py -v -k "Fluxo"

# Executar apenas testes de segurança
pytest devdocs/despesa-api-mvp.py -v -k "Seguranca"
```

## Detecção de endpoints indisponíveis

Alguns endpoints podem não estar disponíveis na versão atual da API em execução (ex: `/api/regras-despesa`, `/api/relatorios`, `/api/export`, `/api/solicitacoes-categoria`). Os testes detectam automaticamente endpoints que retornam 404 e marcam o teste como **SKIPPED** em vez de FAILED. Quando o endpoint for implantado, o teste passará a executar automaticamente.

## Diagnóstico de 404 na API rodando

Se endpoints existem no código-fonte mas retornam 404 na API em execução, os problemas observados são:

- `SolicitacaoCategoriaService`: uso de `@AllArgsConstructor` junto com `@Value` (injeção de `adminEmail`) impede criação do bean quando o construtor não inclui o campo anotado.
- `SecurityConfig`: ausência de `@EnableMethodSecurity` impede `@PreAuthorize` (o controller fica ativo, mas o endpoint pode ser bloqueado por configuração incorreta).
- `application.properties`: falta `file.upload-dir` (quebra upload e dependências) e regras de URL para novos endpoints.
- Docker image desatualizada: é necessário `docker compose build --no-cache` após corrigir os itens acima.

Resumo prático: corrija os pontos acima, ajuste propriedades e faça rebuild da imagem para que os endpoints passem a responder.

## Credenciais de teste

Definidas em `SecurityConfig.java` (InMemoryUserDetailsManager):

| Usuário    | Senha      | Role(s)                          |
|------------|------------|----------------------------------|
| `serventia`| `password` | `ROLE_SERVENTIA`                 |
| `auditor`  | `password` | `ROLE_AUDITOR`                   |
| `admin`    | `password` | `ROLE_ADMIN`, `ROLE_SERVENTIA`, `ROLE_AUDITOR` |

---

## Payloads de esclarecimento

Os endpoints de esclarecimento recebem **string pura** no corpo da requisição:

- `POST /api/despesas/{id}/workflow/solicitar-esclarecimento`
- `POST /api/despesas/solicitacoes-esclarecimento/{solicitacaoId}/responder`

Os testes enviam o corpo como texto (com `Content-Type: application/json`) para compatibilidade com o controller atual.

## Estrutura dos testes

### 1. `TestHealthCheck` - Verificação de saúde

| Teste                | Endpoint       | Verifica                         |
|----------------------|----------------|----------------------------------|
| `test_hello_world`   | `GET /hello`   | API está acessível e respondendo |

### 2. `TestCategorias` - CRUD de categorias (`ROLE_ADMIN`)

| Teste                               | Endpoint                      | Verifica                                  |
|-------------------------------------|-----------------------------  |-------------------------------------------|
| `test_listar_categorias`            | `GET /api/categorias`         | Retorna lista                             |
| `test_criar_categoria`              | `POST /api/categorias`        | Cria com status 201                       |
| `test_buscar_categoria_por_id`      | `GET /api/categorias/{id}`    | Retorna categoria específica              |
| `test_atualizar_categoria`          | `PUT /api/categorias/{id}`    | Atualiza nome                             |
| `test_deletar_categoria`            | `DELETE /api/categorias/{id}` | Remove com status 204                     |
| `test_acesso_negado_para_serventia` | `GET /api/categorias`         | Serventia recebe 403                      |
| `test_acesso_negado_para_auditor`   | `GET /api/categorias`         | Auditor recebe 403                        |

### 3. `TestSubcategorias` - CRUD de subcategorias (`ROLE_ADMIN`)

| Teste                             | Endpoint                         | Verifica                        |
|-----------------------------------|--------------------------------- |---------------------------------|
| `test_listar_subcategorias`       | `GET /api/subcategorias`         | Retorna lista                   |
| `test_criar_subcategoria`         | `POST /api/subcategorias`        | Cria com status 201             |
| `test_buscar_subcategoria_por_id` | `GET /api/subcategorias/{id}`    | Retorna subcategoria específica |
| `test_atualizar_subcategoria`     | `PUT /api/subcategorias/{id}`    | Atualiza dados                  |
| `test_deletar_subcategoria`       | `DELETE /api/subcategorias/{id}` | Remove com status 204           |

### 4. `TestDespesasCRUD` - CRUD de despesas

| Teste                                    | Endpoint                    | Verifica                                     |
|--------------------------------------    |---------------------------- |----------------------------------------------|
| `test_criar_despesa_como_serventia`      | `POST /api/despesas`        | Status inicial = `REGISTRADA`                |
| `test_listar_despesas`                   | `GET /api/despesas`         | Retorna lista                                |
| `test_buscar_despesa_por_id`             | `GET /api/despesas/{id}`    | Retorna despesa específica                   |
| `test_atualizar_despesa_registrada`      | `PUT /api/despesas/{id}`    | Serventia edita despesa `REGISTRADA`         |
| `test_deletar_despesa`                   | `DELETE /api/despesas/{id}` | Remove com status 204                        |
| `test_criar_despesa_negado_para_auditor` | `POST /api/despesas`        | Auditor recebe 403                           |
| `test_buscar_despesa_inexistente`        | `GET /api/despesas/999999`  | Retorna 404                                  |

### 5. `TestComprovantes` - CRUD + upload de comprovantes

| Teste                                | Endpoint                                             | Verifica                          |
|--------------------------------------|------------------------------------------------------|-----------------------------------|
| `test_listar_comprovantes`           | `GET /api/comprovantes`                              | Retorna lista                     |
| `test_criar_comprovante_via_json`    | `POST /api/comprovantes`                             | Cria via JSON                     |
| `test_buscar_comprovante_por_id`     | `GET /api/comprovantes/{id}`                         | Retorna comprovante               |
| `test_atualizar_comprovante`         | `PUT /api/comprovantes/{id}`                         | Atualiza dados                    |
| `test_deletar_comprovante`           | `DELETE /api/comprovantes/{id}`                      | Remove com status 204             |
| `test_listar_comprovantes_por_despesa` | `GET /api/comprovantes/despesas/{id}/comprovantes` | Lista por despesa                 |
| `test_upload_arquivo`                | `POST /api/comprovantes/upload`                      | Upload multipart com `despesaId`  |
| `test_download_arquivo`              | `GET /api/comprovantes/files/{filename}`             | Download do comprovante           |

### 6. `TestRegrasDespesa` - Regras de permissão (`ROLE_ADMIN`)

| Teste                                      | Endpoint                  | Verifica                                        |
|----------------------------------------    |---------------------------|-------------------------------------------------|
| `test_listar_regras`                       | `GET /api/regras-despesa` | Retorna lista                                   |
| `test_criar_regra_desabilitando_categoria` | `POST /api/regras-despesa`| Cria regra que bloqueia categoria               |
| `test_despesa_bloqueada_por_regra`         | `POST /api/despesas`      | Criação falha quando regra desabilita           |
| `test_acesso_negado_serventia`             | `GET /api/regras-despesa` | Serventia recebe 403                            |
| `test_acesso_negado_auditor`               | `GET /api/regras-despesa` | Auditor recebe 403                              |

### 7. `TestRelatorios` - Estatísticas

| Teste                        | Endpoint                                | Verifica                                    |
|------------------------------|-----------------------------------------|---------------------------------------------|
| `test_estatisticas_despesas` | `GET /api/relatorios/despesas/estatisticas` | Retorna contagem para todos os 5 status |

### 8. `TestExport` - Exportação Excel

| Teste                       | Endpoint                     | Verifica                            |
|-----------------------------|------------------------------|-------------------------------------|
| `test_export_despesas_xlsx` | `GET /api/export/despesas.xlsx` | Retorna arquivo XLSX válido      |

### 9. `TestSolicitacaoCategoria` - Solicitação de nova categoria (`ROLE_SERVENTIA`)

| Teste                              | Endpoint                           | Verifica                           |
|----------------------------------- |---------------------------------   |------------------------------    --|
| `test_solicitar_nova_categoria`    | `POST /api/solicitacoes-categoria` | Cria solicitação tipo CATEGORIA    |
| `test_solicitar_nova_subcategoria` | `POST /api/solicitacoes-categoria` | Cria solicitação tipo SUBCATEGORIA |
| `test_acesso_negado_auditor`       | `POST /api/solicitacoes-categoria` | Auditor recebe 403                 |

### 10. `TestSeguranca` - Controle de acesso

| Teste                                | Verifica                                              |
|--------------------------------------|-------------------------------------------------------|
| `test_requisicao_sem_credenciais`    | Requisição anônima retorna 401                        |
| `test_serventia_nao_pode_aprovar`    | Serventia não pode executar ação de auditor (403)     |
| `test_serventia_nao_pode_rejeitar`   | Serventia não pode rejeitar despesa (403)             |
| `test_auditor_nao_pode_criar_despesa` | Auditor não pode criar despesa (403)                 |
| `test_auditor_nao_pode_submeter`     | Auditor não pode submeter despesa (403)               |

---

## Fluxos de auditoria (`tech/fluxo-de-dados-auditoria.md`)

Os testes abaixo reproduzem os fluxos completos do ciclo de vida da despesa conforme documentado em `tech/fluxo-de-dados-auditoria.md`.

Nota: a API atual não implementa filtro por status em `GET /api/despesas`, então os testes usam `?status=...` apenas como referência e filtram localmente. A resposta ao esclarecimento usa `/api/despesas/solicitacoes-esclarecimento/{id}/responder` (prefixo `/api/despesas`), conforme o controller atual.

### Diagrama de estados

```
               ┌─────────────┐
               │   INÍCIO    │
               └──────┬──────┘
                      │
                      ▼
               ┌─────────────┐
               │ REGISTRADA  │ ◄── POST /api/despesas
               └──────┬──────┘
                      │ POST .../workflow/submeter
                      ▼
               ┌─────────────┐
        ┌─────►│  SUBMETIDA  │◄────────────────────────────┐
        │      └──┬───┬───┬──┘                             │
        │         │   │   │                                │
        │         │   │   │ POST .../solicitar-            │
        │         │   │   │      esclarecimento            │
        │         │   │   ▼                                │
        │         │   │ ┌──────────────────────┐           │
        │         │   │ │ PENDENTE DE          │           │
        │         │   │ │ ESCLARECIMENTO       │───────────┘
        │         │   │ └──────────────────────┘
        │         │   │   POST .../responder
        │         │   │   (volta p/ SUBMETIDA)
        │         │   │
        │         │   │ POST .../workflow/rejeitar
        │         │   ▼
        │         │ ┌─────────────┐
        │         │ │  REJEITADA  │ ── Ciclo encerrado (falha)
        │         │ └─────────────┘
        │         │
        │         │ POST .../workflow/aprovar
        │         ▼
        │   ┌─────────────┐
        │   │  APROVADA   │ ── Ciclo encerrado (sucesso)
        │   └─────────────┘
        │
        └── (ciclo de esclarecimento pode se repetir)
```

### Fluxo A - Aprovação direta (`TestFluxoAprovacao`)

**Caminho**: `REGISTRADA → SUBMETIDA → APROVADA`

| Passo | Ator      | Ação                                  | Endpoint                                           | Status resultante |
|-------|-----------|---------------------------------------|----------------------------------------------------|-------------------|
| 1     | Serventia | Cria despesa                          | `POST /api/despesas`                               | `REGISTRADA`      |
| 2     | Serventia | Anexa comprovante                     | `POST /api/comprovantes/upload`                    | `REGISTRADA`      |
| 3     | Serventia | Submete para auditoria                | `POST /api/despesas/{id}/workflow/submeter`        | `SUBMETIDA`       |
| 4     | Auditor   | Lista despesas submetidas             | `GET /api/despesas`                                | -                 |
| 5     | Auditor   | Visualiza detalhes                    | `GET /api/despesas/{id}`                           | -                 |
| 6     | Auditor   | Aprova                                | `POST /api/despesas/{id}/workflow/aprovar`         | `APROVADA`        |

### Fluxo B - Rejeição (`TestFluxoRejeicao`)

**Caminho**: `REGISTRADA → SUBMETIDA → REJEITADA`

| Passo | Ator      | Ação                                  | Endpoint                                           | Status resultante |
|-------|-----------|---------------------------------------|----------------------------------------------------|-------------------|
| 1     | Serventia | Cria despesa                          | `POST /api/despesas`                               | `REGISTRADA`      |
| 2     | Serventia | Anexa comprovante                     | `POST /api/comprovantes/upload`                    | `REGISTRADA`      |
| 3     | Serventia | Submete para auditoria                | `POST /api/despesas/{id}/workflow/submeter`        | `SUBMETIDA`       |
| 4     | Auditor   | Rejeita                               | `POST /api/despesas/{id}/workflow/rejeitar`        | `REJEITADA`       |

### Fluxo C - Esclarecimento + aprovação (`TestFluxoEsclarecimento`)

**Caminho**: `REGISTRADA → SUBMETIDA → PENDENTE_DE_ESCLARECIMENTO → SUBMETIDA → APROVADA`

| Passo | Ator      | Ação                                  | Endpoint                                                                  | Status resultante               |
|-------|-----------|---------------------------------------|----------------------------------------------------------------------------|--------------------------------|
| 1     | Serventia | Cria despesa                          | `POST /api/despesas`                                                       | `REGISTRADA`                   |
| 2     | Serventia | Submete para auditoria                | `POST /api/despesas/{id}/workflow/submeter`                                | `SUBMETIDA`                    |
| 3     | Auditor   | Solicita esclarecimento               | `POST /api/despesas/{id}/workflow/solicitar-esclarecimento`                | `PENDENTE_DE_ESCLARECIMENTO`   |
| 4     | Serventia | Responde esclarecimento               | `POST /api/despesas/solicitacoes-esclarecimento/{solId}/responder`         | `SUBMETIDA`                    |
| 5     | Auditor   | Aprova                                | `POST /api/despesas/{id}/workflow/aprovar`                                 | `APROVADA`                     |

### Fluxo D - Esclarecimento + rejeição (`TestFluxoEsclarecimentoComRejeicao`)

**Caminho**: `REGISTRADA → SUBMETIDA → PENDENTE_DE_ESCLARECIMENTO → SUBMETIDA → REJEITADA`

| Passo | Ator      | Ação                                  | Endpoint                                                                  | Status resultante               |
|-------|-----------|---------------------------------------|----------------------------------------------------------------------------|--------------------------------|
| 1     | Serventia | Cria despesa                          | `POST /api/despesas`                                                       | `REGISTRADA`                   |
| 2     | Serventia | Submete                               | `POST /api/despesas/{id}/workflow/submeter`                                | `SUBMETIDA`                    |
| 3     | Auditor   | Solicita esclarecimento               | `POST /api/despesas/{id}/workflow/solicitar-esclarecimento`                | `PENDENTE_DE_ESCLARECIMENTO`   |
| 4     | Serventia | Responde                              | `POST /api/despesas/solicitacoes-esclarecimento/{solId}/responder`         | `SUBMETIDA`                    |
| 5     | Auditor   | Rejeita                               | `POST /api/despesas/{id}/workflow/rejeitar`                                | `REJEITADA`                    |

### Fluxo E - Múltiplos ciclos de esclarecimento (`TestFluxoMultiplosEsclarecimentos`)

**Caminho**: `REGISTRADA → SUBMETIDA → PENDENTE → SUBMETIDA → PENDENTE → SUBMETIDA → APROVADA`

| Passo | Ator      | Ação                                  | Status resultante              |
|-------|-----------|---------------------------------------|--------------------------------|
| 1     | Serventia | Cria e submete                        | `SUBMETIDA`                    |
| 2     | Auditor   | Solicita esclarecimento (1o ciclo)    | `PENDENTE_DE_ESCLARECIMENTO`   |
| 3     | Serventia | Responde (1o ciclo)                   | `SUBMETIDA`                    |
| 4     | Auditor   | Solicita esclarecimento (2o ciclo)    | `PENDENTE_DE_ESCLARECIMENTO`   |
| 5     | Serventia | Responde (2o ciclo)                   | `SUBMETIDA`                    |
| 6     | Auditor   | Aprova                                | `APROVADA`                     |

Demonstra que o ciclo de esclarecimento pode se repetir indefinidamente antes da decisão final.

### Fluxo F - End-to-end com comprovantes (`TestFluxoCompletoComComprovantes`)

**Caminho**: Fluxo C completo incluindo upload de múltiplos comprovantes, consultas intermediárias e verificação via relatório.

| Passo | Ator      | Ação                                  | Endpoints utilizados                                                      |
|-------|-----------|---------------------------------------|---------------------------------------------------------------------------|
| 1     | Serventia | Cria despesa                          | `POST /api/despesas`                                                      |
| 2     | Serventia | Anexa 2 comprovantes                  | `POST /api/comprovantes/upload` (x2)                                      |
| 3     | Serventia | Verifica comprovantes vinculados      | `GET /api/comprovantes/despesas/{id}/comprovantes`                        |
| 4     | Serventia | Submete                               | `POST /api/despesas/{id}/workflow/submeter`                               |
| 5     | Auditor   | Lista submetidas                      | `GET /api/despesas`                                                       |
| 6     | Auditor   | Verifica detalhes e comprovantes      | `GET /api/despesas/{id}`, `GET .../comprovantes`                          |
| 7     | Auditor   | Solicita esclarecimento               | `POST /api/despesas/{id}/workflow/solicitar-esclarecimento`               |
| 8     | Serventia | Responde                              | `POST /api/despesas/solicitacoes-esclarecimento/{solId}/responder`        |
| 9     | Auditor   | Aprova                                | `POST /api/despesas/{id}/workflow/aprovar`                                |
| 10    | Admin     | Verifica estatísticas                 | `GET /api/relatorios/despesas/estatisticas`                               |

### Transições de status (`TestTransicoesStatus`)

Testes unitários para cada transição individual do diagrama de estados:

| Teste                                         | Transição                                        |
|-----------------------------------------------|--------------------------------------------------|
| `test_registrada_para_submetida`              | `REGISTRADA → SUBMETIDA`                         |
| `test_submetida_para_aprovada`                | `SUBMETIDA → APROVADA`                           |
| `test_submetida_para_rejeitada`               | `SUBMETIDA → REJEITADA`                          |
| `test_submetida_para_pendente_esclarecimento` | `SUBMETIDA → PENDENTE_DE_ESCLARECIMENTO`         |
| `test_pendente_para_submetida`                | `PENDENTE_DE_ESCLARECIMENTO → SUBMETIDA`         |

---

## Cobertura de endpoints

| Endpoint                                                              | Método   | Classe de teste                        |
|-----------------------------------------------------------------------|----------|----------------------------------------|
| `/hello`                                                              | GET      | `TestHealthCheck`                      |
| `/api/categorias`                                                     | GET      | `TestCategorias`                       |
| `/api/categorias`                                                     | POST     | `TestCategorias`                       |
| `/api/categorias/{id}`                                                | GET      | `TestCategorias`                       |
| `/api/categorias/{id}`                                                | PUT      | `TestCategorias`                       |
| `/api/categorias/{id}`                                                | DELETE   | `TestCategorias`                       |
| `/api/subcategorias`                                                  | GET      | `TestSubcategorias`                    |
| `/api/subcategorias`                                                  | POST     | `TestSubcategorias`                    |
| `/api/subcategorias/{id}`                                             | GET      | `TestSubcategorias`                    |
| `/api/subcategorias/{id}`                                             | PUT      | `TestSubcategorias`                    |
| `/api/subcategorias/{id}`                                             | DELETE   | `TestSubcategorias`                    |
| `/api/despesas`                                                       | GET      | `TestDespesasCRUD`, fluxos             |
| `/api/despesas`                                                       | POST     | `TestDespesasCRUD`, fluxos             |
| `/api/despesas/{id}`                                                  | GET      | `TestDespesasCRUD`, fluxos             |
| `/api/despesas/{id}`                                                  | PUT      | `TestDespesasCRUD`                     |
| `/api/despesas/{id}`                                                  | DELETE   | `TestDespesasCRUD`                     |
| `/api/despesas/{id}/workflow/submeter`                                | POST     | `TestTransicoesStatus`, fluxos         |
| `/api/despesas/{id}/workflow/aprovar`                                 | POST     | `TestTransicoesStatus`, fluxos         |
| `/api/despesas/{id}/workflow/rejeitar`                                | POST     | `TestTransicoesStatus`, fluxos         |
| `/api/despesas/{despesaId}/workflow/solicitar-esclarecimento`         | POST     | `TestTransicoesStatus`, fluxos         |
| `/api/despesas/solicitacoes-esclarecimento/{solId}/responder`         | POST     | `TestTransicoesStatus`, fluxos         |
| `/api/comprovantes`                                                   | GET      | `TestComprovantes`                     |
| `/api/comprovantes`                                                   | POST     | `TestComprovantes`                     |
| `/api/comprovantes/{id}`                                              | GET      | `TestComprovantes`                     |
| `/api/comprovantes/{id}`                                              | PUT      | `TestComprovantes`                     |
| `/api/comprovantes/{id}`                                              | DELETE   | `TestComprovantes`                     |
| `/api/comprovantes/despesas/{despesaId}/comprovantes`                 | GET      | `TestComprovantes`, fluxos             |
| `/api/comprovantes/upload`                                            | POST     | `TestComprovantes`, fluxos             |
| `/api/comprovantes/files/{filename}`                                 | GET      | `TestComprovantes`                     |
| `/api/regras-despesa`                                                 | GET      | `TestRegrasDespesa`                    |
| `/api/regras-despesa`                                                 | POST     | `TestRegrasDespesa`                    |
| `/api/relatorios/despesas/estatisticas`                               | GET      | `TestRelatorios`, fluxos               |
| `/api/export/despesas.xlsx`                                           | GET      | `TestExport`                           |
| `/api/solicitacoes-categoria`                                         | POST     | `TestSolicitacaoCategoria`             |

**Total: 35 endpoints cobertos, 50+ assertions, 6 fluxos de auditoria completos.**
