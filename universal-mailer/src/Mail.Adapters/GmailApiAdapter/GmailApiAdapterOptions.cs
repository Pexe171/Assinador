using System.Collections.Generic;

namespace UniversalMailer.Mail.Adapters.GmailApiAdapter;

/// <summary>
/// Configurações específicas do adapter Gmail API.
/// </summary>
public sealed class GmailApiAdapterOptions
{
    public string ProjectId { get; init; } = string.Empty;

    public string CredentialsPath { get; init; } = string.Empty;

    public IReadOnlyCollection<string> Scopes { get; init; } = new List<string>();

    public string PubSubSubscription { get; init; } = string.Empty;
}
