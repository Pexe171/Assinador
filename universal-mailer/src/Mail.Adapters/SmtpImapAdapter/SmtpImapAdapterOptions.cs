using System.Collections.Generic;

namespace UniversalMailer.Mail.Adapters.SmtpImapAdapter;

/// <summary>
/// Configurações específicas para autenticação e monitoramento SMTP/IMAP.
/// </summary>
public sealed class SmtpImapAdapterOptions
{
    public string SmtpHost { get; init; } = string.Empty;

    public int SmtpPort { get; init; } = 587;

    public bool UseStartTls { get; init; } = true;

    public string ImapHost { get; init; } = string.Empty;

    public int ImapPort { get; init; } = 993;

    public bool UseImapSsl { get; init; } = true;

    public string OAuthClientId { get; init; } = string.Empty;

    public string OAuthClientSecret { get; init; } = string.Empty;

    public IReadOnlyCollection<string> OAuthScopes { get; init; } = new List<string>();

    public string TrackingPrefix { get; init; } = "AC-";
}
