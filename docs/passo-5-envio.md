# Passo 5 — Envio (Cliente + Engine)

Este passo integra a interface WPF com a engine de envio para realizar disparos de e-mail usando os dados informados pela operação, sem enriquecimentos automáticos. O foco está em garantir a prévia obrigatória, gerar o identificador `AC-####` e registrar todos os metadados do envio.

## 1. Componentes criados

| Projeto | Destaques |
|---------|-----------|
| `Client.Wpf` | Formulário MVVM com campos de cliente, destinatários, valores adicionais, CC/BCC, pré-visualização obrigatória e botão de envio. |
| `Engine` | Serviço `MailDispatcher` responsável por gerar a prévia, renderizar templates `.html/.oft`, chamar o `IMailProvider` e registrar o envio. |
| `Mail.Adapters` | Implementação `FileSystemMailProvider` para desenvolvimento, gravando os envios em `logs/outbox`. |
| `Persistence` | `FileMailDispatchStore` que salva `messageId`, `threadId`, versão do template e destinatários em `db/mail-dispatch-log.jsonl`. |

## 2. Fluxo de envio

1. A operação preenche os campos obrigatórios e adicionais no cliente WPF.
2. O botão **Pré-visualizar** gera o HTML final usando o template `validacao_renda`, incluindo o ID `AC-####` e exibindo o assunto composto.
3. Somente após uma prévia válida o botão **Enviar** é habilitado. Qualquer alteração nos campos invalida a prévia.
4. O `MailDispatcher` chama o `IMailProvider.Send()` da conta selecionada. No ambiente local usamos o `FileSystemMailProvider`, que registra o conteúdo em arquivo `.eml`.
5. O envio é persistido via `FileMailDispatchStore`, guardando `messageId`, `threadId`, versão do template e listas de Para/CC/BCC.

## 3. Configuração

* `config/mail.providers.json` define as contas disponíveis e o provedor associado. No modo local, a pasta `logs/outbox` recebe os arquivos `.eml` gerados.
* `templates/templates.json` lista os templates disponíveis. O corpo HTML está em `templates/validacao_renda_body.html`.
* Os arquivos de template são copiados automaticamente para a pasta de saída do cliente WPF.

## 4. Próximos passos

1. Implementar provedores reais (Graph, SMTP/IMAP, Gmail) respeitando o contrato `IMailProvider`.
2. Conectar o armazenamento a um banco relacional via `Persistence` quando o serviço Windows for criado.
3. Adicionar testes automatizados para garantir a integridade dos placeholders e o registro de envios.
4. Incluir anexos e suporte a múltiplos templates por fluxo.
