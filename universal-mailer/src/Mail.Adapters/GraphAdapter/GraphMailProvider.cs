using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Mail.Adapters.Common;

namespace UniversalMailer.Mail.Adapters.GraphAdapter;

/// <summary>
/// Adapter para Microsoft Graph. Implementa envio, monitoramento via webhook e rastreamento por messageId.
/// </summary>
public sealed class GraphMailProvider : IMailProvider
{
    private readonly IGraphMailClient _client;
    private readonly GraphMailAdapterOptions _options;
    private readonly ILogger<GraphMailProvider> _logger;

    public GraphMailProvider(
        IGraphMailClient client,
        IOptions<GraphMailAdapterOptions> options,
        ILogger<GraphMailProvider> logger)
    {
        _client = client ?? throw new ArgumentNullException(nameof(client));
        _options = options?.Value ?? throw new ArgumentNullException(nameof(options));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public Task<MailOperationResult> SendAsync(SendMessageRequest request, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Enviando mensagem via Graph para {Account}", request.Account.AccountId);
        return _client.SendAsync(request, cancellationToken);
    }

    public Task<MailOperationResult> SaveDraftAsync(SaveDraftRequest request, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Salvando rascunho via Graph para {Account}", request.Account.AccountId);
        return _client.SaveDraftAsync(request, cancellationToken);
    }

    public Task<MailMessage?> GetMessageAsync(GetMessageRequest request, CancellationToken cancellationToken = default)
    {
        return _client.GetMessageAsync(request, cancellationToken);
    }

    public Task<IReadOnlyList<MailMessage>> ListInboxAsync(ListInboxRequest request, CancellationToken cancellationToken = default)
    {
        return _client.ListInboxAsync(request, cancellationToken);
    }

    public Task<MailOperationResult> ReplyAllAsync(ReplyAllRequest request, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Respondendo a todos via Graph para {Account}", request.Account.AccountId);
        return _client.ReplyAllAsync(request, cancellationToken);
    }

    public Task<MailTrackingInfo> TrackIdAsync(TrackMessageRequest request, CancellationToken cancellationToken = default)
    {
        return _client.TrackIdAsync(request, cancellationToken);
    }
}
