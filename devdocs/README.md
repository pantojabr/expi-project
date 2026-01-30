Ao subir o container `despesa_app`, o banco de dados será automaticamente populado com as categorias e subcategorias definidas em `data.sql`.

### Problemas comuns: `data.sql` não executa

Em versões recentes do Spring Boot, a execução automática de `data.sql` **não é habilitada por padrão** para bancos não-embutidos (ex.: PostgreSQL). Isso pode fazer o script não rodar mesmo sem erro.

Para garantir a execução do seed, confirme estas propriedades (em `application.properties` ou variáveis de ambiente):

- `spring.sql.init.mode=always` (força a execução em bancos externos)
- `spring.jpa.defer-datasource-initialization=true` (garante que as tabelas sejam criadas antes do `data.sql`)

Após ajustar, reconstrua e suba novamente:

```bash
docker compose down
docker compose build app
docker compose up -d
```

Como validar que o seed rodou:

- Verifique nos logs da aplicação algo como: `Executing SQL script from class path resource [data.sql]`
- Cheque no banco as tabelas `categoria`, `subcategoria`, `tipo_cartorio`, `serventia_extrajudicial`, `serventia_tipo_cartorio`, `usuario_dominio`.

Se o banco já tinha dados, `data.sql` ainda roda, mas inserts duplicados podem falhar (e você verá erros no log). Nesse caso, limpe o banco ou ajuste o seed para evitar duplicidade.
