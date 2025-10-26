using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Core.Returns.Models;

/// <summary>
/// Representa uma mensagem de retorno capturada de um provedor de e-mail.
/// </summary>
public sealed record ReturnMessage(
    string ProviderMessageId,
    string AccountId,
    MailProviderType ProviderType,
    MailParticipant Sender,
    string Subject,
    string Body,
    DateTimeOffset ReceivedAt,
    string? ConversationId,
    IReadOnlyDictionary<string, string>? Metadata
);
