# Passo 3 — Adapters de Provedor

Este documento detalha como o Assinador passa a conversar com qualquer provedor de e-mail usando um contrato único e adapters especializados.

## 1. Contrato universal (`IMailProvider`)

* Reside em `src/Core/Mail/Contracts`.
* Define as operações críticas: `Send`, `SaveDraft`, `GetMessage`, `ListInbox`, `ReplyAll` e `TrackId`.
* Padroniza envelopes, participantes, corpo, anexos e resultados para que o domínio não dependa das particularidades de cada provedor.

## 2. Modelagem de requests e resultados

* `MailAccount` agrega a conta e o `MailProviderDescriptor`, que descreve tipo e configurações específicas.
* `MailOperationResult` e `MailTrackingInfo` trazem status, IDs do provedor e metadados, permitindo telemetria estruturada.
* Todos os métodos são assíncronos, preparados para I/O intensivo e resilient.

## 3. Registro e roteamento

* `MailProviderRegistry` registra fábricas por `MailProviderType` (Graph, SMTP/IMAP ou Gmail API).
* `MailAccountRouter` recebe o mapa de contas e resolve automaticamente o adapter correto.
* O roteamento por conta usa o campo `provider` no `mail.providers.json`.

## 4. Adapters implementados

### 4.1 Graph (`GraphMailProvider`)

* Usa um `IGraphMailClient` para encapsular o `GraphServiceClient`.
* Suporta envio, rascunho, webhook push e rastreio por `messageId`.
* Log estruturado para cada operação.

### 4.2 SMTP/IMAP (`SmtpImapMailProvider`)

* Conecta com qualquer provedor via MailKit.
* Garante token de rastreio `AC-####` no assunto + cabeçalho `Message-Id`.
* Expõe opções para SMTP, IMAP e OAuth2.

### 4.3 Gmail API (`GmailApiMailProvider`)

* Opcional, preparado para Pub/Sub de baixa latência.
* Encapsula chamadas via `IGmailApiClient` e permite customizações por `GmailApiAdapterOptions`.

## 5. Configuração

O arquivo `universal-mailer/config/mail.providers.json` agora inclui o campo `provider` para cada caixa postal, permitindo que a engine carregue as opções corretas:

```json
{
  "nome": "financeiro",
  "provider": "smtp-imap",
  "host": "smtp.exemplo.com",
  "tracking": {
    "prefix": "AC-"
  }
}
```

## 6. Próximos passos

1. Implementar clientes concretos (`GraphServiceClient`, MailKit e Gmail API) seguindo os contratos.
2. Conectar o `MailAccountRouter` ao carregamento de configuração (`IOptions` + `mail.providers.json`).
3. Adicionar testes de integração simulando envios e retornos em cada provedor.
