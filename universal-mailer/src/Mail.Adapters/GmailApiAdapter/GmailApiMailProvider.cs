using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Mail.Adapters.GmailApiAdapter;

/// <summary>
/// Adapter para a API nativa do Gmail. Mantém compatibilidade com Pub/Sub para baixa latência.
/// </summary>
public sealed class GmailApiMailProvider : IMailProvider
{
    private readonly IGmailApiClient _client;
    private readonly GmailApiAdapterOptions _options;
    private readonly ILogger<GmailApiMailProvider> _logger;

    public GmailApiMailProvider(
        IGmailApiClient client,
        IOptions<GmailApiAdapterOptions> options,
        ILogger<GmailApiMailProvider> logger)
    {
        _client = client ?? throw new ArgumentNullException(nameof(client));
        _options = options?.Value ?? throw new ArgumentNullException(nameof(options));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public Task<MailOperationResult> SendAsync(SendMessageRequest request, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Enviando mensagem pela Gmail API para {Account}", request.Account.AccountId);
        return _client.SendAsync(request, cancellationToken);
    }

    public Task<MailOperationResult> SaveDraftAsync(SaveDraftRequest request, CancellationToken cancellationToken = default)
    {
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
        return _client.ReplyAllAsync(request, cancellationToken);
    }

    public Task<MailTrackingInfo> TrackIdAsync(TrackMessageRequest request, CancellationToken cancellationToken = default)
    {
        return _client.TrackIdAsync(request, cancellationToken);
    }
}
