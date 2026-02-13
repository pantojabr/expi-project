Impacto no seu código com SigNoz (sem aplicar mudanças), olhando seu projeto atual:

- API: Spring Boot 3.2.2 em `despesa-api-mvp/pom.xml`
- Front: Next 16.1.4 em `despesas-front-mvp/package.json`

**1) Backend Spring (`despesa-api-mvp`)**
Menor impacto: usar **OpenTelemetry Java Agent** (sem mexer em código Java).

Arquivos que mudariam:
1. `despesa-api-mvp/Dockerfile` (ou comando de start) para incluir `-javaagent`
2. `despesa-api-mvp/docker-compose.yml` (ou env da infra) para variáveis `OTEL_*`
3. Opcional: `despesa-api-mvp/src/main/resources/application.properties` só para naming/metadata extra

Exemplo do que entraria no start:
```bash
java -javaagent:/otel/opentelemetry-javaagent.jar -jar app.jar
```

Exemplo de envs:
```bash
OTEL_SERVICE_NAME=despesa-api
OTEL_EXPORTER_OTLP_ENDPOINT=http://<host-otel-ou-signoz>:4318
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=dev,service.version=0.0.1
```

Resumo de impacto backend:
- Código Java: praticamente zero
- Build/deploy: pequeno ajuste no runtime

**2) Frontend Next.js (`despesas-front-mvp`)**
Impacto pequeno, mas há mudança de código.

Arquivos que mudariam:
1. `despesas-front-mvp/package.json` (novas deps OTel)
2. `despesas-front-mvp/instrumentation.ts` (arquivo novo, no root)
3. `despesas-front-mvp/.env.local` (ou env no deploy)

Como ficaria (conceitualmente) `instrumentation.ts`:
```ts
import { registerOTel } from "@vercel/otel";

export function register() {
  registerOTel({ serviceName: process.env.OTEL_SERVICE_NAME ?? "despesas-front" });
}
```

Env típico:
```bash
OTEL_SERVICE_NAME=despesas-front
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://<host-otel-ou-signoz>:4318/v1/traces
```

Resumo de impacto frontend:
- 1 arquivo novo + deps
- sem refactor de páginas/componentes

**3) Observação importante (React no browser)**
Se você quiser rastreio de interações no browser (RUM-like), aí o impacto cresce:
- inicialização OTel web no cliente
- atenção a CORS no collector
- mais cuidado com volume de telemetria

**4) Estimativa de esforço no seu repo**
1. Fase mínima (server-side only): 0 refactor de regra de negócio
2. Arquivos tocados: ~4 a 6
3. Risco de regressão funcional: baixo (maior risco é configuração de endpoint/env)

Nenhuma mudança foi feita ainda.

Fontes:
- SigNoz Java/Spring: https://signoz.io/docs/instrumentation/java/opentelemetry-java/
- SigNoz Next.js: https://signoz.io/docs/instrumentation/javascript/opentelemetry-nextjs/
- Next instrumentation: https://nextjs.org/docs/pages/api-reference/file-conventions/instrumentation
- Spring observability: https://docs.spring.io/spring-boot/reference/actuator/observability.html
- OTel JS status (browser): https://opentelemetry.io/docs/languages/js/

Se quiser, no próximo passo eu te entrego um "plano de patch" com diff por arquivo (`Dockerfile`, `docker-compose`, `instrumentation.ts`, `.env`) sem aplicar nada ainda.
