# Blueprint Inicial do Assinador

Este blueprint sintetiza as principais decisões de arquitetura do Passo 1, detalhando responsabilidades, integrações e princípios orientadores.

## 1. Visão Geral

O Assinador será composto por uma engine de serviço Windows, uma API REST e um cliente WPF, todos apoiados por módulos reutilizáveis. A solução será construída em C# com .NET 8, permitindo aproveitar worker services, hosting genérico e bibliotecas modernas para integrações com provedores de e-mail.

## 2. Componentes Principais

### 2.1 Core

* Define entidades, agregados, value objects e serviços de domínio.
* Consolida validações (FluentValidation) e regras para templates de e-mail.
* Expõe interfaces para que camadas externas implementem integrações, mantendo o domínio independente.

### 2.2 Mail.Adapters

* Implementa conectores para Microsoft Graph, Gmail API, SMTP e IMAP.
* Adota padrões Adapter e Strategy para selecionar o provedor adequado por cenário.
* Fornece mecanismos de resiliência (circuit breaker, retry com Polly) alinhados às políticas do Core.

### 2.3 Watcher

* Responsável por ouvir eventos de entrada: webhooks do Graph, IMAP IDLE ou polling.
* Normaliza notificações e encaminha para o Core, disparando processamentos assíncronos.
* Operará como hosted service dentro da engine Windows.

### 2.4 Persistence

* Usa EF Core com migrations versionadas.
* SQLite garantirá leveza em desenvolvimento; PostgreSQL será adotado em produção.
* Fornece repositórios e consultas otimizadas (LINQ + DDD Specification Pattern quando necessário).

### 2.5 Api

* ASP.NET Minimal APIs para simplicidade e performance.
* Versionamento via rotas e suporte a autenticação (JWT + IdentityServer ou Azure AD, a definir no Passo 2).
* Disponibiliza endpoints para operação (envio, consulta, reprocessamento) e administração.

### 2.6 Client.Wpf

* Interface desktop com MVVM, injeção de dependência (CommunityToolkit.Mvvm) e componentes reativos.
* Consome a API para disparar envios, acompanhar retornos, visualizar históricos e gerenciar usuários/configurações.

### 2.7 Jobs

* Conjunto de worker services responsáveis por tarefas programadas: monitoramento de SLA, follow-ups automáticos, limpeza de logs, backups.
* Integração com Windows Task Scheduler ou Hangfire (modo background) conforme necessidade.

## 3. Princípios de Engenharia

1. **Separação clara de responsabilidades:** cada projeto com fronteiras bem definidas e contratos explícitos.
2. **Configuração centralizada:** uso de `IOptions`, variáveis de ambiente e appsettings versionados.
3. **Observabilidade desde o início:** logging estruturado (Serilog), métricas (OpenTelemetry) e rastreamento distribuído.
4. **Testes em múltiplos níveis:** testes de unidade (Core), integração (Adapters/Persistence) e ponta a ponta (API + Cliente).
5. **Automação:** pipelines CI/CD com build, testes, análise estática e empacotamento.

## 4. Entregáveis do Próximo Passo

1. Criar a solution e os projetos vazios com referências corretas.
2. Configurar pacotes básicos (Serilog, EF Core, CommunityToolkit.Mvvm, Polly).
3. Definir convenções de código (estilo C# 12, analisadores Roslyn) e documentação de APIs com OpenAPI.

Este blueprint será expandido à medida que avançarmos para os próximos passos, incorporando diagramas, fluxos de processos e decisões técnicas adicionais.
