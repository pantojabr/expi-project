# ADR-001 Issue: CORS "Invalid CORS request"

## O Problema
Ao tentar acessar a aplicação Web via navegador, recebia-se o erro `Invalid CORS request` (HTTP 403 Forbidden) do backend Spring Boot, mesmo com o frontend configurado para usar um proxy (rewrite) no Next.js (`/api/:path*` -> `http://localhost:8080/api/:path*`).

## Causa Raiz
1.  **Arquitetura Same-Origin:** A ADR-001 define que o frontend e o backend devem parecer estar na mesma origem para o navegador. O Next.js atua como um Reverse Proxy para isso.
2.  **Comportamento do Navegador:** Mesmo em requisições same-origin (ou proxied), o navegador pode enviar o cabeçalho `Origin` (especialmente em requisições mutantes como POST/PUT ou se o proxy repassar o header original).
3.  **Restrição do Backend:** O `SecurityConfig.java` estava configurado rigidamente para aceitar apenas `http://localhost:3000`.
4.  **O Gatilho:** O acesso local estava sendo feito via `http://127.0.0.1:3000`. Para o Spring Security (e para a spec CORS), `localhost` e `127.0.0.1` são origens distintas. O backend rejeitava a requisição porque `http://127.0.0.1:3000` não estava na lista permitida.

## Solução Aplicada
Alteramos o `SecurityConfig.java` para usar `allowedOriginPatterns` com wildcards para ambientes locais, abrangendo tanto `localhost` quanto IPs de loopback em qualquer porta:

```java
configuration.setAllowedOriginPatterns(List.of("http://localhost:*", "http://127.0.0.1:*"));
```

Isso desbloqueou o desenvolvimento permitindo que o navegador acesse a aplicação de qualquer variação de host local.

## TODO: Aprimoramento Futuro e Segurança (Produção)

A configuração atual (`http://localhost:*`, `http://127.0.0.1:*`) é **insegura para produção** se o servidor estiver exposto publicamente e **não é a prática profissional ideal** (hardcoded).

### Por que não foi feito via Variável de Ambiente agora?
Para agilidade na resolução do bloqueio de desenvolvimento (MVP), optou-se pela alteração direta no código. A introdução de variáveis de ambiente exige alteração no `application.properties`, no `docker-compose.yml` e potencialmente na esteira de CI/CD, o que aumentaria a complexidade da correção imediata.

### Plano de Ação para Produção
1.  **Externalizar Configuração:** Substituir a lista hardcoded por uma injeção via `application.properties`:
    ```java
    @Value("${cors.allowed-origins}")
    private List<String> allowedOrigins;
    ```
2.  **Variáveis de Ambiente:** No ambiente de produção (Docker/K8s), definir `CORS_ALLOWED_ORIGINS` contendo apenas o domínio real de produção (ex: `https://app.exofi.tjap.jus.br`).
3.  **Revisão da Arquitetura de Proxy:** Verificar se o Reverse Proxy de produção (NGINX/Ingress) está configurado para remover o cabeçalho `Origin` ou reescrevê-lo, garantindo que o backend receba apenas tráfego confiável, tornando o CORS no nível da aplicação uma camada de defesa em profundidade, não a única barreira.
