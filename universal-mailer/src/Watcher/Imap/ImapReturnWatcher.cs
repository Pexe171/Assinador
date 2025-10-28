using System.Linq;
using Microsoft.Extensions.Logging;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Core.Returns.Processing;
using UniversalMailer.Mail.Adapters.Common;
using UniversalMailer.Mail.Adapters.SmtpImapAdapter;
using UniversalMailer.Watcher.Common;

namespace UniversalMailer.Watcher.Imap;

/// <summary>
/// Realiza polling periódico em contas IMAP para capturar novos retornos.
/// </summary>
public sealed class ImapReturnWatcher
{
    private readonly MailAccountRouter _accountRouter;
    private readonly ISmtpImapClient _imapClient;
    private readonly ReturnMessageProcessor _processor;
    private readonly ImapWatcherOptions _options;
    private readonly ILogger<ImapReturnWatcher>? _logger;
    private readonly Dictionary<string, DateTimeOffset> _lastSeen = new(StringComparer.OrdinalIgnoreCase);

    public ImapReturnWatcher(
        MailAccountRouter accountRouter,
        ISmtpImapClient imapClient,
        ReturnMessageProcessor processor,
        ImapWatcherOptions options,
        ILogger<ImapReturnWatcher>? logger = null)
    {
        _accountRouter = accountRouter ?? throw new ArgumentNullException(nameof(accountRouter));
        _imapClient = imapClient ?? throw new ArgumentNullException(nameof(imapClient));
        _processor = processor ?? throw new ArgumentNullException(nameof(processor));
        _options = options ?? throw new ArgumentNullException(nameof(options));
        _logger = logger;
    }

    public async Task<IReadOnlyList<ReturnProcessingResult>> PollAsync(CancellationToken cancellationToken = default)
    {
        var results = new List<ReturnProcessingResult>();

        foreach (var accountId in _options.AccountIds)
        {
            cancellationToken.ThrowIfCancellationRequested();

            var account = _accountRouter.GetAccount(accountId);
            var since = GetSince(accountId);
            var request = new ListInboxRequest(account, since, unreadOnly: true);
            var messages = await _imapClient.ListInboxAsync(request, cancellationToken).ConfigureAwait(false);

            if (messages.Count == 0)
            {
                continue;
            }

            foreach (var message in messages.OrderBy(m => m.CreatedAt))
            {
                cancellationToken.ThrowIfCancellationRequested();

                var returnMessage = ReturnMessageFactory.FromMailMessage(account, message);
                var result = await _processor.ProcessAsync(returnMessage, cancellationToken).ConfigureAwait(false);
                results.Add(result);
                _lastSeen[accountId] = message.CreatedAt;

                _logger?.LogInformation(
                    "Retorno IMAP processado: conta {AccountId}, tracking {Tracking}, status {Status}.",
                    accountId,
                    result.Record.TrackingKey,
                    result.Record.Status);
            }
        }

        return results;
    }

    public async Task RunAsync(CancellationToken cancellationToken = default)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                await PollAsync(cancellationToken).ConfigureAwait(false);
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Falha ao processar retornos IMAP.");
            }

            try
            {
                await Task.Delay(_options.PollInterval, cancellationToken).ConfigureAwait(false);
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                break;
            }
        }
    }

    private DateTimeOffset GetSince(string accountId)
    {
        if (_lastSeen.TryGetValue(accountId, out var timestamp))
        {
            return timestamp;
        }

        if (_options.InitialSince.HasValue)
        {
            return _options.InitialSince.Value;
        }

        return DateTimeOffset.UtcNow - _options.DefaultLookback;
    }
}
