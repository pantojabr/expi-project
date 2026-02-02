# ADR-001 — Manter _same-origin_ para Web e expor API via **path** para eliminar CORS

**Status:** Aprovado  
**Data:** 31/01/2026  
**Decisores:** Time do projeto  
**Contexto:** Arquitetura Web + API com Gateway/BFF e autenticação via JWT (Resource Server)

---

## Contexto e problema

A aplicação Web (executando em navegador) precisa consumir endpoints da plataforma (Gateway/BFF/serviços). Em arquitetura com domínios distintos, por exemplo:

* `https://app.exemplo.com` (frontend)
* `https://api.exemplo.com` (gateway/bff)

o navegador ativa a política **Same-Origin** e exige **CORS** para permitir requisições JavaScript. Isso introduz complexidade operacional e de diagnóstico:

* necessidade de configurar CORS no ponto exposto ao browser (Gateway)
* preflight `OPTIONS` frequente (especialmente com header `Authorization`)
* erros típicos “funciona no Postman, falha no browser”
* necessidade de testes específicos (preflight + headers)
* aumento de superfície de configuração e manutenção

Observação importante: **BFF não elimina CORS**. CORS é consequência de **origem (scheme + host + port)** e é **enforcement do navegador**; o servidor apenas “autoriza” via headers.

---

## Decisão

**Manter o frontend Web e a API do Web sob a mesma origem (_same-origin_)**, expondo a API como **path** no mesmo host do frontend:

* Frontend: `https://app.exemplo.com/`
* API Web (Gateway → BFF Web): `https://app.exemplo.com/api/web/**`
* (opcional) API Mobile: `https://app.exemplo.com/api/mobile/**` _(CORS não é relevante para mobile, mas padroniza roteamento)_

O tráfego interno permanece:

`Gateway → BFF → serviços`

por rede interna, sem exposição direta ao navegador.

---

## Consequências

### Benefícios (positivos)

* **Elimina CORS para Web** (sem preflight, sem headers CORS, sem falhas específicas do browser)
* Reduz complexidade de configuração e suporte
* Facilita diagnósticos (erros reais aparecem como HTTP 401/403/5xx, não “CORS error”)
* Simplifica testes automatizados e pipelines (menos casos especiais)
* Mantém a arquitetura modular (Gateway e BFF continuam existindo; apenas muda a “fronteira” exposta ao browser)

### Custos / trade-offs (negativos)

* Exige **reverse proxy**/roteamento por path no edge (NGINX, Cloudflare, Ingress, etc.)
* CDN e cache precisam ser configurados com cuidado para não cachear respostas de API indevidamente
* Regras de segurança por path (ex.: `/api/**`) devem ser bem definidas para evitar exposição acidental

---

## Alternativas consideradas

### A1) Subdomínio separado para API (`api.exemplo.com`)

**Rejeitada** para o caso Web principal por:

* CORS obrigatório + preflight
* maior custo operacional e risco de misconfiguração
* complexidade não compensada quando o consumidor Web é o principal

### A2) Domínio totalmente separado

**Rejeitada** por ser ainda mais sensível e raramente necessária no contexto atual.

### A3) Configurar CORS “bem feito” e seguir com subdomínio

**Possível**, mas escolhido apenas se houver motivação forte (ex.: múltiplos frontends independentes/terceiros). No momento, seria custo sem retorno.

---

## Implicações de segurança

* **CORS não é um mecanismo de segurança de API**; é um mecanismo de segurança do browser.
* A segurança da API permanece baseada em:
    * TLS/HTTPS
    * autenticação/autorização via JWT (Resource Server)
    * rate limiting / WAF / logs no Gateway
* Ao manter same-origin, evitamos “falsa segurança” por CORS e mantemos controle real por autenticação/autorização.

---

## Plano de implementação

1. Publicar o frontend em `https://app.exemplo.com/`
2. Configurar edge/reverse proxy para rotear:
    * `/api/web/**` → Gateway (ou diretamente para BFF, conforme arquitetura)
3. Garantir que BFF/serviços não sejam expostos diretamente à internet
4. Validar que o Web funciona sem CORS e sem preflight (verificação via DevTools → Network)
5. Atualizar documentação de rotas e guidelines de deploy

---

## Critérios de revisão

Reavaliar esta decisão se:

* surgirem consumidores Web em domínios terceiros (parceiros, widgets, multi-tenant externo)
* for necessário expor API pública
* houver exigência de separação rígida de domínios por governança corporativa

---

## Notas finais

Esta ADR reduz **complexidade acidental** sem remover modularidade: Gateway e BFF continuam válidos, mas o Web consome a API via **path** na mesma origem, eliminando CORS e seus custos associados no ambiente de navegador.

* * *