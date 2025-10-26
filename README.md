# Assinador — Visão Geral Inicial

Este repositório está sendo preparado para receber o novo ecossistema do Assinador, uma plataforma pensada para orquestrar envios de e-mail transacionais, acompanhar retornos e automatizar processos de assinatura digital. Este documento apresenta o primeiro passo da nossa jornada: definição da linguagem, das formas de execução e da divisão em módulos.

## Linguagem e Plataforma

* **Stack principal:** C# com .NET 8, escolhidos pela maturidade, suporte de longo prazo e integração fluida com Windows Services, APIs REST e clientes WPF.
* **Paradigma:** orientação a objetos com apoio de conceitos funcionais quando fizer sentido (ex.: LINQ), sempre priorizando código limpo, SOLID e testes automatizados desde as camadas de domínio.

## Formas de Execução

1. **Serviço Windows (engine):** processo contínuo responsável por integrar com provedores de e-mail, manter conexões com webhooks/IMAP e oferecer endpoints REST internos para orquestração.
2. **Cliente desktop WPF:** interface rica para os times operacionais e administrativos acompanharem envios, retornos, históricos e configurações avançadas.
   * A mesma API REST permitirá futuramente um **cliente web** em React, sem duplicar regras.

## Módulos e Responsabilidades

| Projeto | Responsabilidade | Observações |
|---------|------------------|-------------|
| `Core` | Núcleo de domínio, validações, regras de negócio, templates e contratos. | Exporá serviços e entidades puras, além de value objects reutilizáveis. |
| `Mail.Adapters` | Integrações com Graph, Gmail API, SMTP/IMAP e provedores futuros. | Aplicaremos o padrão Adapter + Strategy para permitir múltiplos canais. |
| `Watcher` | Conexões reativas (Graph webhooks, IMAP IDLE, polling de fallback). | Executará dentro do serviço Windows, monitorando eventos de entrada. |
| `Persistence` | Acesso a dados com EF Core. SQLite para desenvolvimento, PostgreSQL para produção. | Isolamento via repositórios e migrations versionadas. |
| `Api` | API REST pública para o cliente WPF e integrações externas. | ASP.NET Minimal APIs com autenticação e versionamento. |
| `Client.Wpf` | Aplicação desktop para operação e administração. | MVVM, bindings fortes e componentes reutilizáveis. |
| `Jobs` | Rotinas agendadas (SLA, follow-ups, limpeza, backups). | Hospedadas em worker services e integradas ao scheduler do Windows. |

## Próximos Passos

1. Criar a solution `.sln` com todos os projetos vazios, definindo referências entre camadas conforme as responsabilidades.
2. Documentar padrões de configuração (appsettings, secrets, logging estruturado) para garantir consistência entre serviços.
3. Configurar automações iniciais (CI/CD, linting, testes) para assegurar qualidade desde o início.
4. Padronizar templates transacionais seguindo o [Passo 4 — Template e Corpo do E-mail](docs/passo-4-template-email.md).

## Banco de Dados e API REST

O ecossistema agora conta com uma API REST (`src/Api`) construída sobre **ASP.NET Minimal APIs** e um banco relacional gerenciado via **EF Core**. Os principais pontos:

* **Persistência:** SQLite por padrão (`Database:Provider = "sqlite"`), com suporte imediato a PostgreSQL bastando alterar `appsettings.json` para `"postgres"` e apontar `ConnectionString`. As migrations vivem em `src/Persistence/Migrations` e garantem o mesmo schema em ambos os bancos.
* **Envio de e-mails:** endpoint `POST /emails/send` processa templates armazenados no banco, renderiza variáveis e dispara via provedor cadastrado (FileSystem por padrão).
* **Consultas:**
  * `GET /emails/{protocolo}` recupera detalhes de um envio.
  * `GET /returns/{protocolo}` retorna o histórico consolidado de retornos.
  * `GET /search` permite localizar envios e retornos por protocolo, e-mail ou status.
* **Administração:**
  * `GET|POST|PUT|DELETE /admin/templates` para versionar templates HTML.
  * `GET|POST|PUT|DELETE /admin/providers` para cadastrar provedores e contas (incluindo diretórios de saída do FileSystem).

Para rodar localmente:

```bash
cd universal-mailer
dotnet run --project src/Api/Api.csproj
```

O Swagger ficará disponível em `/swagger` quando executado em modo Development.

## Entregas em andamento

* Passo 5 — Envio concluído: cliente WPF, engine e provedor de arquivos conectados para gerar prévias obrigatórias, disparar via `IMailProvider` e registrar `messageId`/`threadId`. Detalhes no [Passo 5 — Envio](docs/passo-5-envio.md).
* Passo 6 — Acompanhamento multi-provedor: monitoramento de retornos via webhook do Graph e polling IMAP, classificação automática (VALIDADO/INVALIDADO/COMPLEMENTAR/DUPLO/MANUAL) com base em palavras-chave e persistência em `FileReturnStore`, além de job de SLA para marcar ATENÇÃO/VENCIDO e disparar follow-up usando a mesma conta de envio.

Para detalhes adicionais e decisões de design, consulte o documento em `docs/blueprint-inicial.md`.
