using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Core.Returns.Models;

/// <summary>
/// Registro persistido de uma mensagem de retorno já processada.
/// </summary>
public sealed record ReturnRecord(
    string TrackingKey,
    bool HasValidTrackingId,
    string ProviderMessageId,
    string AccountId,
    MailProviderType ProviderType,
    MailParticipant Sender,
    string Subject,
    string BodyPreview,
    ReturnClassification Classification,
    DateTimeOffset ReceivedAt,
    string? ConversationId,
    IReadOnlyDictionary<string, string>? Metadata)
{
    public ReturnStatus Status => Classification.Status;
}
