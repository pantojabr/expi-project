# Query - Categorias Aninhadas

```sql
WITH cat_sub AS (
  SELECT
    c.id AS categoria_id,
    c.nome AS categoria_nome,
    s.id AS subcategoria_id,
    s.nome AS subcategoria_nome,
    ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY s.nome, s.id) AS rn
  FROM categoria c
  LEFT JOIN subcategoria s ON s.categoria_id = c.id
)
SELECT
  CASE WHEN rn = 1 THEN categoria_nome ELSE '' END AS categoria,
  COALESCE(subcategoria_nome, '') AS subcategoria
FROM cat_sub
ORDER BY categoria_nome, subcategoria_nome;
```

```sql
-- Filtro opcional por nome (Categoria ou Subcategoria)
-- WHERE (
--   LOWER(c.nome) LIKE '%' || LOWER(:termo) || '%'
--   OR LOWER(s.nome) LIKE '%' || LOWER(:termo) || '%'
-- )
```

## Analise detalhada da query

1. 🧱 **CTE `cat_sub`**: centraliza a juncao entre `categoria` e `subcategoria` e prepara os campos para a exibicao final. Isso deixa o `SELECT` final simples e legivel.
2. 🔗 **`LEFT JOIN`**: garante que categorias sem subcategorias aparecam na tabela, com `subcategoria` vazia.
3. 🧮 **`ROW_NUMBER()` por categoria**: cria um contador por categoria ordenado por nome da subcategoria. Esse numero e usado para mostrar o nome da categoria apenas na primeira linha do grupo.
4. 🪪 **`CASE WHEN rn = 1`**: imprime o nome da categoria somente na primeira linha; nas demais linhas do mesmo grupo, retorna string vazia.
5. 🧼 **`COALESCE(subcategoria_nome, '')`**: evita `NULL` e deixa a celula vazia quando nao ha subcategoria.
6. 🧭 **`ORDER BY categoria_nome, subcategoria_nome`**: organiza a exibicao de modo previsivel e agrupado por categoria.
7. 🔎 **Filtro opcional por nome**: ao aplicar o `WHERE`, tanto categorias quanto subcategorias passam a influenciar o resultado, alinhado com o filtro da interface.

## CTE (Common Table Expression) 🧠

A CTE (expressao comum de tabela) e uma forma de dar nome a uma subquery e reutilizar o resultado logo em seguida. Ela melhora a legibilidade e organiza a query em etapas.

**Exemplo simples de CTE:**
```sql
WITH base AS (
  SELECT id, nome
  FROM categoria
)
SELECT *
FROM base
ORDER BY nome;
```

**Por que usar aqui?**
- ✅ deixa a query principal limpa
- ✅ permite calcular `ROW_NUMBER()` uma vez
- ✅ facilita evoluir a logica sem duplicar codigo

## Tutorial didatico: entendendo a query passo a passo

Abaixo vai um caminho natural para entender a query, do basico ao avancado, com exemplos intermediarios. 🧭

### 1) Entendendo as tabelas e o relacionamento (Basico) 🧩
**Conceito:** `categoria` e `subcategoria` tem relacionamento 1:N (uma categoria pode ter varias subcategorias).

**Query basica (somente categorias):**
```sql
SELECT id, nome
FROM categoria
ORDER BY nome;
```

**Query basica (somente subcategorias):**
```sql
SELECT id, nome, categoria_id
FROM subcategoria
ORDER BY categoria_id, nome;
```

### 2) Juntando as duas tabelas (Basico → Medio) 🔗
**Conceito:** `JOIN` conecta registros de duas tabelas.

**Query intermediaria com `INNER JOIN`:**
```sql
SELECT
  c.nome AS categoria,
  s.nome AS subcategoria
FROM categoria c
JOIN subcategoria s ON s.categoria_id = c.id
ORDER BY c.nome, s.nome;
```
**O que acontece:** categorias sem subcategoria nao aparecem.

**Query intermediaria com `LEFT JOIN`:**
```sql
SELECT
  c.nome AS categoria,
  s.nome AS subcategoria
FROM categoria c
LEFT JOIN subcategoria s ON s.categoria_id = c.id
ORDER BY c.nome, s.nome;
```
**O que acontece:** categorias sem subcategoria aparecem com `subcategoria = NULL`.

### 3) Tratando `NULL` na exibicao (Medio) 🧼
**Conceito:** `COALESCE` troca `NULL` por um valor padrao.

```sql
SELECT
  c.nome AS categoria,
  COALESCE(s.nome, '') AS subcategoria
FROM categoria c
LEFT JOIN subcategoria s ON s.categoria_id = c.id
ORDER BY c.nome, s.nome;
```

### 4) Numerando subcategorias por categoria (Medio → Avancado) 🧮
**Conceito:** `ROW_NUMBER()` cria um contador por grupo (`PARTITION BY`).

```sql
SELECT
  c.nome AS categoria,
  s.nome AS subcategoria,
  ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY s.nome, s.id) AS rn
FROM categoria c
LEFT JOIN subcategoria s ON s.categoria_id = c.id
ORDER BY c.nome, s.nome;
```
**O que acontece:** cada subcategoria ganha um numero por categoria.

### 5) Mostrar a categoria apenas uma vez (Avancado) 🪪
**Conceito:** `CASE` para condicionar exibicao.

```sql
WITH cat_sub AS (
  SELECT
    c.id AS categoria_id,
    c.nome AS categoria_nome,
    s.id AS subcategoria_id,
    s.nome AS subcategoria_nome,
    ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY s.nome, s.id) AS rn
  FROM categoria c
  LEFT JOIN subcategoria s ON s.categoria_id = c.id
)
SELECT
  CASE WHEN rn = 1 THEN categoria_nome ELSE '' END AS categoria,
  COALESCE(subcategoria_nome, '') AS subcategoria
FROM cat_sub
ORDER BY categoria_nome, subcategoria_nome;
```
**O que acontece:** para cada categoria, apenas a primeira linha traz o nome dela.

### 6) Filtro por nome (Medio) 🔎
**Conceito:** filtrar por texto em categoria ou subcategoria.

```sql
WITH cat_sub AS (
  SELECT
    c.id AS categoria_id,
    c.nome AS categoria_nome,
    s.id AS subcategoria_id,
    s.nome AS subcategoria_nome,
    ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY s.nome, s.id) AS rn
  FROM categoria c
  LEFT JOIN subcategoria s ON s.categoria_id = c.id
  WHERE (
    LOWER(c.nome) LIKE '%' || LOWER(:termo) || '%'
    OR LOWER(s.nome) LIKE '%' || LOWER(:termo) || '%'
  )
)
SELECT
  CASE WHEN rn = 1 THEN categoria_nome ELSE '' END AS categoria,
  COALESCE(subcategoria_nome, '') AS subcategoria
FROM cat_sub
ORDER BY categoria_nome, subcategoria_nome;
```

### 7) Resumo por nivel de conhecimento 📌
- 🟢 **Basico:** `SELECT`, `ORDER BY`, entender 1:N, `JOIN`.
- 🟡 **Medio:** `LEFT JOIN`, `COALESCE`, filtros com `LIKE`.
- 🔵 **Avancado:** `CTE`, `ROW_NUMBER()` com `PARTITION BY`, `CASE` para exibicao controlada.

## Observacoes e ajustes (PostgreSQL) 🛠️

### 1) Nome do CTE (evitar palavra reservada) ⚠️
Em PostgreSQL, `JOINED` pode conflitar ou gerar confusao por ser proximo de palavras reservadas. Uma alternativa segura e usar um nome como `base` ou `cat_sub`.

**Exemplo com CTE renomeado:**
```sql
WITH cat_sub AS (
  SELECT
    c.id AS categoria_id,
    c.nome AS categoria_nome,
    s.id AS subcategoria_id,
    s.nome AS subcategoria_nome,
    ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY s.nome, s.id) AS rn
  FROM categoria c
  LEFT JOIN subcategoria s ON s.categoria_id = c.id
)
SELECT
  CASE WHEN rn = 1 THEN categoria_nome ELSE '' END AS categoria,
  COALESCE(subcategoria_nome, '') AS subcategoria
FROM cat_sub
ORDER BY categoria_nome, subcategoria_nome;
```

### 2) `NULLS LAST` no `ORDER BY` 📌
Se `subcategoria_nome` puder ser `NULL`, o PostgreSQL pode ordenar `NULL` antes das strings. Para forcar `NULL` no fim:
```sql
ORDER BY categoria_nome, subcategoria_nome NULLS LAST;
```
Isso evita que categorias sem subcategoria aparecam no topo do grupo.

### 3) Otimizacoes de indice (PostgreSQL) ⚡
Se o volume crescer, esses indices ajudam bastante:

**Para o `JOIN`:**
```sql
CREATE INDEX IF NOT EXISTS idx_subcategoria_categoria_id
ON subcategoria (categoria_id);
```

**Para filtros por nome (LIKE):**
```sql
CREATE INDEX IF NOT EXISTS idx_categoria_nome
ON categoria (nome);

CREATE INDEX IF NOT EXISTS idx_subcategoria_nome
ON subcategoria (nome);
```

**Para buscas com `LIKE '%termo%'` (trigram):**
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_categoria_nome_trgm
ON categoria USING gin (nome gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_subcategoria_nome_trgm
ON subcategoria USING gin (nome gin_trgm_ops);
```
Esses indices sao muito eficientes para buscas parciais no Postgres.
