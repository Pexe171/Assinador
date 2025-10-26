namespace UniversalMailer.Core.Mail.Models;

/// <summary>
/// Resultado retornado pelo provedor após o envio.
/// </summary>
public sealed record MailSendResult(string MessageId, string? ThreadId, DateTimeOffset SentAt)
{
    public string MessageId { get; } = MessageId;

    public string? ThreadId { get; } = ThreadId;

    public DateTimeOffset SentAt { get; } = SentAt;
}
