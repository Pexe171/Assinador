namespace UniversalMailer.Core.Mail.Models;

/// <summary>
/// Dados necessários para efetuar o envio via provedor.
/// </summary>
public sealed class MailSendRequest
{
    public MailSendRequest(MailAccount account, MailEnvelope envelope, MailContent content, string trackingId)
    {
        Account = account ?? throw new ArgumentNullException(nameof(account));
        Envelope = envelope ?? throw new ArgumentNullException(nameof(envelope));
        Content = content ?? throw new ArgumentNullException(nameof(content));
        TrackingId = string.IsNullOrWhiteSpace(trackingId)
            ? throw new ArgumentException("O identificador de rastreamento é obrigatório.", nameof(trackingId))
            : trackingId;
    }

    public MailAccount Account { get; }

    public MailEnvelope Envelope { get; }

    public MailContent Content { get; }

    public string TrackingId { get; }
}
