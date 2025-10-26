using System;
using System.Collections.Generic;
using System.IO;

namespace UniversalMailer.Core.Mail.Contracts;

/// <summary>
/// Enumera os tipos de provedores suportados nativamente.
/// </summary>
public enum MailProviderType
{
    Graph,
    SmtpImap,
    GmailApi
}

/// <summary>
/// Representa a configuração de uma caixa postal gerenciada pelo sistema.
/// </summary>
/// <param name="AccountId">Identificador interno da conta.</param>
/// <param name="Address">Endereço de e-mail completo.</param>
/// <param name="DisplayName">Nome amigável utilizado no envio.</param>
/// <param name="Provider">Informações sobre o provedor utilizado.</param>
/// <param name="Metadata">Dicionário para configurações específicas adicionais.</param>
public sealed record MailAccount(string AccountId, string Address, string? DisplayName, MailProviderDescriptor Provider, IReadOnlyDictionary<string, string>? Metadata = null);

/// <summary>
/// Metadados mínimos para instanciar um adapter.
/// </summary>
/// <param name="Name">Nome lógico do provedor.</param>
/// <param name="Type">Tipo de provedor (Graph, SMTP/IMAP, etc.).</param>
/// <param name="Settings">Coleção de configurações específicas.</param>
public sealed record MailProviderDescriptor(string Name, MailProviderType Type, IReadOnlyDictionary<string, string> Settings);

/// <summary>
/// Envelope padrão de uma mensagem.
/// </summary>
public sealed record MailEnvelope(
    MailParticipant From,
    IReadOnlyCollection<MailParticipant> To,
    IReadOnlyCollection<MailParticipant> Cc,
    IReadOnlyCollection<MailParticipant> Bcc,
    string Subject,
    MailPriority Priority = MailPriority.Normal
);

/// <summary>
/// Define a prioridade da mensagem.
/// </summary>
public enum MailPriority
{
    Low,
    Normal,
    High
}

/// <summary>
/// Participante de uma conversa de e-mail.
/// </summary>
public sealed record MailParticipant(string Address, string? Name);

/// <summary>
/// Corpo da mensagem contendo versões em texto e HTML.
/// </summary>
public sealed record MailBody(string? Text, string? Html, IReadOnlyDictionary<string, string>? Headers = null);

/// <summary>
/// Anexo da mensagem.
/// </summary>
public sealed record MailAttachment(string FileName, string ContentType, Func<Stream> ContentFactory, long? ContentLength = null);

/// <summary>
/// Representa uma mensagem armazenada ou retornada pelo provedor.
/// </summary>
public sealed record MailMessage(
    string ProviderMessageId,
    MailEnvelope Envelope,
    MailBody Body,
    IReadOnlyCollection<MailAttachment> Attachments,
    DateTimeOffset CreatedAt,
    string? ThreadId = null,
    IReadOnlyDictionary<string, string>? Headers = null,
    IReadOnlyDictionary<string, string>? ProviderMetadata = null
);

/// <summary>
/// Solicitação de envio.
/// </summary>
public sealed record SendMessageRequest(MailAccount Account, MailMessage DraftMessage);

/// <summary>
/// Solicitação de gravação de rascunho.
/// </summary>
public sealed record SaveDraftRequest(MailAccount Account, MailMessage DraftMessage);

/// <summary>
/// Solicitação de leitura de mensagem por ID.
/// </summary>
public sealed record GetMessageRequest(MailAccount Account, string ProviderMessageId, bool IncludeAttachments = true);

/// <summary>
/// Solicitação de listagem da caixa de entrada.
/// </summary>
public sealed record ListInboxRequest(
    MailAccount Account,
    DateTimeOffset? Since = null,
    int? PageSize = null,
    bool UnreadOnly = false,
    string? ConversationId = null,
    string? TrackingToken = null
);

/// <summary>
/// Solicitação de responder a todos.
/// </summary>
public sealed record ReplyAllRequest(MailAccount Account, string ProviderMessageId, MailBody ReplyBody, IReadOnlyCollection<MailAttachment>? Attachments = null);

/// <summary>
/// Solicitação de acompanhamento via ID rastreável.
/// </summary>
public sealed record TrackMessageRequest(MailAccount Account, string TrackingId, IReadOnlyDictionary<string, string>? Criteria = null);

/// <summary>
/// Resultado padrão para operações de e-mail.
/// </summary>
public sealed record MailOperationResult(
    MailOperationStatus Status,
    string? ProviderMessageId,
    string? TrackingId,
    string? Error,
    IReadOnlyDictionary<string, string>? Metadata
)
{
    public bool IsSuccess => Status == MailOperationStatus.Succeeded;

    public static MailOperationResult Success(string providerMessageId, string? trackingId = null, IReadOnlyDictionary<string, string>? metadata = null)
        => new(MailOperationStatus.Succeeded, providerMessageId, trackingId, null, metadata);

    public static MailOperationResult Deferred(string providerMessageId, string? trackingId = null, IReadOnlyDictionary<string, string>? metadata = null)
        => new(MailOperationStatus.Deferred, providerMessageId, trackingId, null, metadata);

    public static MailOperationResult Failure(string? error, string? providerMessageId = null, string? trackingId = null, IReadOnlyDictionary<string, string>? metadata = null)
        => new(MailOperationStatus.Failed, providerMessageId, trackingId, error, metadata);

    public static MailOperationResult NotSupported(string? error = null)
        => new(MailOperationStatus.NotSupported, null, null, error, null);
}

/// <summary>
/// Status operacional.
/// </summary>
public enum MailOperationStatus
{
    Succeeded,
    Deferred,
    Failed,
    NotSupported
}

/// <summary>
/// Resultado de rastreamento de mensagem.
/// </summary>
public sealed record MailTrackingInfo(bool Found, string? ProviderMessageId, string? ConversationId, IReadOnlyDictionary<string, string>? Metadata = null)
{
    public static MailTrackingInfo NotFound() => new(false, null, null, null);
}
