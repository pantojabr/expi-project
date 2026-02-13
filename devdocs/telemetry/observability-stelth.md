# Observability Stealth Mode (SigNoz + OTel)

Este modo roda por `run/run-despesas-api.sh` e injeta observabilidade sem alterar o funcionamento padrão do projeto.

## Objetivo

- Não editar os arquivos base de `despesa-api-mvp/` e `despesas-front-mvp/` em runtime.
- Aplicar observabilidade em uma cópia efêmera no `/tmp`.
- Permitir subir/parar/rebuild com um único comando.

## Arquivos criados

- `run/run-despesas-api.sh`
- `run/run-signoz.sh`
- `run/stealth/Dockerfile`
- `run/stealth/docker-compose.yml`
- `run/stealth/instrumentation.ts`
- `run/stealth/next.config.ts`
- `run/stealth/.env`
- `run/stealth/otel-collector-config.yaml`

## Como funciona (stealth)

1. O script cria workspace isolado em `/tmp/despesas-stealth-work`.
2. Copia o backend e frontend originais para esse workspace.
3. Injeta os overrides somente na cópia:
   - API: `Dockerfile.stealth` (com Java Agent OTel)
   - Front: `instrumentation.ts` (Next.js + `@vercel/otel`)
   - Front: `next.config.ts` (rewrite `/api` para `http://api:8080` dentro da rede Docker)
4. Sobe os containers via `run/stealth/docker-compose.yml` usando `run/stealth/.env`.
5. O collector local recebe OTLP e imprime traces no log (`debug exporter`), sem depender de stack externa.
   - O receiver OTLP escuta em `0.0.0.0:4317` e `0.0.0.0:4318` para aceitar tráfego entre containers.

Com isso, o projeto original não precisa “saber” desse modo de operação.

## Comandos

```bash
# sobe stack stealth (build + start)
run/run-despesas-api.sh up

# sobe SigNoz e conecta o stealth nele
run/run-despesas-api.sh up-signoz

# status
run/run-despesas-api.sh ps

# logs
run/run-despesas-api.sh logs

# rebuild completo da cópia efêmera
run/run-despesas-api.sh rebuild

# derruba stack
run/run-despesas-api.sh down
```

## Serviços e portas

Definidos em `run/stealth/.env`:

- Frontend: `localhost:3300`
- API: `localhost:8180`
- Postgres: `localhost:5543`
- OTLP HTTP (collector local): `localhost:14318`
- OTLP gRPC (collector local): `localhost:14317`
- SigNoz UI (quando usado `up-signoz`): `localhost:18080` (padrão stealth)
- SigNoz OTLP HTTP: `localhost:4318`
- SigNoz OTLP gRPC: `localhost:4317`

## Configuração de telemetria

`run/stealth/.env` já inclui:

- `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318`
- `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`
- `OTEL_SERVICE_NAME_API=despesa-api-stealth`
- `OTEL_SERVICE_NAME_FRONT=despesas-front-stealth`

Para enviar ao SigNoz depois, troque `OTEL_EXPORTER_OTLP_ENDPOINT` para o endpoint OTLP do seu ambiente.
No modo `up-signoz`, o script já usa `SIGNOZ_OTLP_ENDPOINT` (padrão `http://host.docker.internal:4318`).
Também usa `SIGNOZ_UI_PORT` (padrão `18080`) para evitar conflito com serviços locais em `8080`.

## SigNoz completo

`run/run-signoz.sh` usa o deploy oficial do SigNoz em `/tmp/signoz`:

```bash
run/run-signoz.sh up
run/run-signoz.sh ps
run/run-signoz.sh logs
run/run-signoz.sh down
```

## Detalhes por componente

### API (Spring)

`run/stealth/Dockerfile`:

- Faz build Maven igual ao fluxo normal.
- Baixa `opentelemetry-javaagent.jar`.
- Inicia com `-javaagent:/otel/opentelemetry-javaagent.jar`.

Impacto no código Java: nenhum.

### Front (Next.js)

`run/stealth/instrumentation.ts`:

- Registra OTel com `registerOTel`.
- Nome de serviço via `OTEL_SERVICE_NAME`.

No compose, o serviço front instala `@vercel/otel` sem persistir no repositório (`npm install --no-save`).

## Observações

- Esse modo é isolado, mas usa Docker local (precisa daemon ativo).
- O script pode usar `rsync`; se não existir, faz fallback para `cp -a`.
- O `/tmp/despesas-stealth-work` pode ser removido manualmente quando quiser.
- O compose stealth adiciona `host.docker.internal:host-gateway` em `api` e `front` para resolver o endpoint OTLP em Linux.
- A cópia stealth ignora `despesas-front-mvp/node_modules`, `despesas-front-mvp/.next` e `despesa-api-mvp/target` para evitar conflitos de permissão e reduzir volume.
- `SQL_INIT_MODE` está em `never` para evitar erro de chave duplicada (`data.sql`) ao reiniciar com volume do Postgres já populado.
- Se quiser reseed de dados iniciais, rode `run/run-despesas-api.sh down`, remova o volume `postgres_data_stealth` e suba com `SQL_INIT_MODE=always` temporariamente.
- O front stealth usa `FRONT_API_REWRITE_BASE_URL=http://api:8080` para que `/api/*` funcione de dentro do container.
- Com o collector local ativo, erros de `Connection refused` para OTLP deixam de ocorrer mesmo sem SigNoz instalado.
