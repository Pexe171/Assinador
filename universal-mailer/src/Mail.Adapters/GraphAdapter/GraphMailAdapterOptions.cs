using System.Collections.Generic;

namespace UniversalMailer.Mail.Adapters.GraphAdapter;

/// <summary>
/// Opções específicas para configuração do adapter Graph.
/// </summary>
public sealed class GraphMailAdapterOptions
{
    public string TenantId { get; init; } = string.Empty;

    public string ClientId { get; init; } = string.Empty;

    public string ClientSecret { get; init; } = string.Empty;

    public IReadOnlyCollection<string> Scopes { get; init; } = new List<string>();

    public string WebhookNotificationUrl { get; init; } = string.Empty;
}
