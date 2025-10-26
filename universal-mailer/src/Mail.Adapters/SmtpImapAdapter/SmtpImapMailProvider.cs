using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Mail.Adapters.SmtpImapAdapter;

/// <summary>
/// Adapter genérico para provedores compatíveis com SMTP OAuth2 e IMAP (MailKit).
/// Utiliza o cabeçalho Message-Id combinado ao subject com prefixo AC-#### para rastrear.
/// </summary>
public sealed class SmtpImapMailProvider : IMailProvider
{
    private readonly ISmtpImapClient _client;
    private readonly SmtpImapAdapterOptions _options;
    private readonly ILogger<SmtpImapMailProvider> _logger;

    public SmtpImapMailProvider(
        ISmtpImapClient client,
        IOptions<SmtpImapAdapterOptions> options,
        ILogger<SmtpImapMailProvider> logger)
    {
        _client = client ?? throw new ArgumentNullException(nameof(client));
        _options = options?.Value ?? throw new ArgumentNullException(nameof(options));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public Task<MailOperationResult> SendAsync(SendMessageRequest request, CancellationToken cancellationToken = default)
    {
        EnsureTrackingToken(request.DraftMessage);
        _logger.LogInformation("Enviando via SMTP/IMAP para {Account}", request.Account.AccountId);
        return _client.SendAsync(request, cancellationToken);
    }

    public Task<MailOperationResult> SaveDraftAsync(SaveDraftRequest request, CancellationToken cancellationToken = default)
    {
        EnsureTrackingToken(request.DraftMessage);
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
        _logger.LogInformation("Respondendo a todos via SMTP/IMAP para {Account}", request.Account.AccountId);
        return _client.ReplyAllAsync(request, cancellationToken);
    }

    public Task<MailTrackingInfo> TrackIdAsync(TrackMessageRequest request, CancellationToken cancellationToken = default)
    {
        return _client.TrackByHeadersAsync(request, cancellationToken);
    }

    private void EnsureTrackingToken(MailMessage message)
    {
        if (message.ProviderMetadata is not null && message.ProviderMetadata.ContainsKey("tracking"))
        {
            return;
        }

        var subject = message.Envelope.Subject;
        if (!subject.Contains(_options.TrackingPrefix, StringComparison.OrdinalIgnoreCase))
        {
            _logger.LogDebug("Sujeito sem token de rastreio detectado. Prefixo {Prefix} será aplicado futuramente no compose.", _options.TrackingPrefix);
        }
    }
}
