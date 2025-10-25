# Arquitetura da Aplicação Desktop

Este documento descreve a arquitetura proposta para o Assinador Desktop, um
cliente moderno para mapeamento de grupos do Telegram com foco em usabilidade,
observabilidade e extensibilidade. O conteúdo está dividido em camadas para
facilitar a compreensão do domínio e de aspectos técnicos.

## Visão Geral

- **Interface Gráfica**: PyQt6, com componentes customizados e suporte a modo
  escuro. A janela principal possui abas para Dashboard, Contas e Logs, além de
  lista lateral de sessões.
- **Backend**: Python 3.11+, organizado em módulos coesos. Comunicação com
  Telegram via Telethon, persistência com SQLAlchemy e execução assíncrona com
  `threading` + `queue`.
- **Banco de Dados**: SQLite embarcado localizado em diretório do usuário. Uso
  do SQLAlchemy ORM para versionamento e abstração.
- **Notificações**: Integração com `plyer` para utilizar o sistema nativo
  (Windows, macOS, Linux).
- **Autoatualização**: Módulo dedicado para consulta e aplicação de updates
  incrementais (detalhado adiante).

## Estrutura de Pastas

```
TelegramManager/
├── main.py              # Ponto de entrada Qt
├── core/                # Regras de negócio e orquestração
│   ├── automation.py    # Motor de automação e tarefas agendadas
│   ├── container.py     # Injeção de dependências
│   ├── database.py      # Conexão com SQLite
│   ├── session_manager.py
│   └── telegram_client.py
├── ui/                  # Camada de apresentação com PyQt6
│   ├── main_window.py   # Janela principal
│   └── widgets/         # Componentes customizados
├── utils/               # Utilitários (configuração, helpers, workers)
├── notifications/       # Integração com sistema operacional
├── storage/             # Modelos ORM
├── updater/             # Autoatualização e integridade
└── assets/              # Ícones e temas (planejado)
```

## Camada de Interface (GUI)

- **MainWindow**: Janela principal com abas (Dashboard, Contas, Logs) e painel
  lateral de contas. Utiliza `QStackedWidget` para detalhes de sessão.
- **DashboardWidget**: Mostra métricas em tempo real usando *signals* do backend.
- **SessionFormWidget**: Formulário humanizado para autenticar contas com 2FA,
  acionando o fluxo de login do Telethon.
- **LogConsoleWidget**: Exibe o log central, facilitando suporte.
- **Tray Icon**: (pendente) permite minimizar para bandeja com ações rápidas.

## Core e Serviços

- **Container**: Contêiner de dependências simples (`core/container.py`).
- **SessionManager**: Persistência e estado das sessões conectadas, com
  restauração planejada (`core/session_manager.py`).
- **TelegramClientPool**: Pool de conexões Telethon para autenticação e
  operações críticas (`core/telegram_client.py`).
- **AutomationEngine**: Registra tarefas, mantém cache ordenado de agendamentos e
  sincroniza progresso com a interface (`core/automation.py`).
- **BackgroundWorker**: Fila de execução assíncrona em `utils/async_worker.py`,
  ideal para evitar travamentos na UI.

## Persistência

- **Database**: Configura o SQLite em diretório controlado pelo usuário.
- **Models**: `Account` e `ExtractionJob` com timestamps. Novas entidades podem
  ser adicionadas facilmente com migrations (ex.: Alembic).
- **Repositories** (futuro): Camada para encapsular consultas complexas.

## Fluxo de Autenticação

1. Usuário informa telefone e nome da conta.
2. `SessionFormWidget` chama `SessionManager.register_session`.
3. O gerente de sessões aciona o `TelegramClientPool` para iniciar o login.
4. Códigos 2FA são solicitados via diálogo modal.
5. Sessão persistida em `sessions_dir` com backup automático.

## Mapeamento de Grupos

- Extração executada em `BackgroundWorker` para evitar travar a UI.
- Barra de progresso atualizada por *signals* Qt.
- Pré-visualização antes de exportar.
- Exportações suportam CSV/JSON/Excel com `pandas` (planejado).

## Autoatualização

- Módulo `TelegramManager/updater/auto_updater.py` verifica periodicamente um endpoint
  seguro (HTTPS) em busca de novas versões.
- Downloads validados com checksum e assinatura digital.
- Atualizações aplicadas após confirmação do usuário, com rollback automático
  em caso de falha.

## Qualidade e Observabilidade

- Logging centralizado com rotação diária.
- Métricas enviadas para `DashboardWidget` via *signals* Qt, facilitando a
  visualização centralizada do progresso.
- Testes unitários com `pytest` e `pytest-qt`.
- Pipeline CI com lint (ruff), type checking (mypy) e testes.

## Roadmap Futuro

- Integração com sistema de notificações avançado (Toast no Windows, Notificações
  interativas no macOS).
- Implementação do módulo de autoatualização completo.
- Suporte a plugins para mapear diferentes tipos de comunidades.
- Internacionalização (i18n) com Qt Linguist.
