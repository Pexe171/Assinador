# Assinador Desktop

Aplicação desktop moderna para gerenciar múltiplas contas do Telegram e executar
mapeamentos de grupos com alto nível de observabilidade. Construída com Python e
PyQt6, integra Telethon, SQLAlchemy e notificações nativas do sistema
operacional.

## Principais Recursos

- Interface com abas (Dashboard, Contas e Logs) e painel lateral para troca
  rápida entre contas.
- Autenticação de contas com suporte a 2FA e persistência de sessões.
- Execução de tarefas assíncronas usando *threads* e filas para evitar travamentos.
- Console de logs em tempo real dentro da própria interface.
- Exportação planejada para CSV/JSON/Excel a partir dos dados mapeados.
- Notificações nativas via `plyer` e suporte a execução em *background*.
- Módulo de autoatualização com validação de integridade.

## Novidades da versão 1.5 (Automação)

- Sistema de automação completo com motor em segundo plano e monitoramento em tempo real.
- Agendador visual de tarefas com sincronização instantânea com o dashboard.
- Relatórios básicos alimentados pelos dados da automação e das extrações recentes.
- Melhorias de performance na listagem de tarefas agendadas, reduzindo reordenações desnecessárias.

## Arquitetura

A arquitetura completa está detalhada em [`docs/arquitetura.md`](docs/arquitetura.md).

## Notas de versão

- [Versão 1.5 — Automação](docs/releases/versao-1.5.md)

## Configuração do Ambiente

1. Instale Python 3.11 ou superior e crie um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\\Scripts\\activate   # Windows
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure variáveis de ambiente do Telegram (API ID e HASH).

## Execução

```bash
python -m TelegramManager.main
```

## Testes

```bash
pytest
```

## Build

A distribuição pode ser gerada com ferramentas como PyInstaller ou Briefcase.
O módulo `TelegramManager/updater/auto_updater.py` prevê atualizações incrementais após a
instalação inicial.
