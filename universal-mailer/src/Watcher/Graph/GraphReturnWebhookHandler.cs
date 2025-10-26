using Microsoft.Extensions.Logging;
using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Core.Returns.Processing;
using UniversalMailer.Mail.Adapters.Common;
using UniversalMailer.Mail.Adapters.GraphAdapter;
using UniversalMailer.Watcher.Common;

namespace UniversalMailer.Watcher.Graph;

/// <summary>
/// Processa notificações push do Graph para identificar retornos de validação.
/// </summary>
public sealed class GraphReturnWebhookHandler
{
    private readonly MailAccountRouter _accountRouter;
    private readonly IGraphMailClient _graphClient;
    private readonly ReturnMessageProcessor _processor;
    private readonly ILogger<GraphReturnWebhookHandler>? _logger;

    public GraphReturnWebhookHandler(
        MailAccountRouter accountRouter,
        IGraphMailClient graphClient,
        ReturnMessageProcessor processor,
        ILogger<GraphReturnWebhookHandler>? logger = null)
    {
        _accountRouter = accountRouter ?? throw new ArgumentNullException(nameof(accountRouter));
        _graphClient = graphClient ?? throw new ArgumentNullException(nameof(graphClient));
        _processor = processor ?? throw new ArgumentNullException(nameof(processor));
        _logger = logger;
    }

    public async Task<ReturnProcessingResult?> HandleAsync(GraphWebhookNotification notification, CancellationToken cancellationToken = default)
    {
        if (notification is null)
        {
            throw new ArgumentNullException(nameof(notification));
        }

        cancellationToken.ThrowIfCancellationRequested();

        var account = _accountRouter.GetAccount(notification.AccountId);
        var request = new GetMessageRequest(account, notification.MessageId);
        var message = await _graphClient.GetMessageAsync(request, cancellationToken).ConfigureAwait(false);

        if (message is null)
        {
            _logger?.LogWarning("Mensagem {MessageId} não encontrada no Graph para a conta {AccountId}.", notification.MessageId, notification.AccountId);
            return null;
        }

        var returnMessage = ReturnMessageFactory.FromMailMessage(account, message);
        var result = await _processor.ProcessAsync(returnMessage, cancellationToken).ConfigureAwait(false);

        _logger?.LogInformation(
            "Retorno processado via Graph: Tracking {TrackingKey}, Status {Status}, Duplicado: {Duplicate}.",
            result.Record.TrackingKey,
            result.Record.Status,
            result.IsDuplicate);

        return result;
    }
}
