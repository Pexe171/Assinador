using System.Linq;
using Microsoft.Extensions.Logging;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Core.Returns.Contracts;
using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Mail.Adapters.Common;

namespace UniversalMailer.Jobs.FollowUp;

/// <summary>
/// Envia follow-ups utilizando o mesmo provedor associado à conta original.
/// </summary>
public sealed class MailReturnFollowUpDispatcher : IReturnFollowUpDispatcher
{
    private readonly MailAccountRouter _accountRouter;
    private readonly ILogger<MailReturnFollowUpDispatcher>? _logger;

    public MailReturnFollowUpDispatcher(MailAccountRouter accountRouter, ILogger<MailReturnFollowUpDispatcher>? logger = null)
    {
        _accountRouter = accountRouter ?? throw new ArgumentNullException(nameof(accountRouter));
        _logger = logger;
    }

    public async Task<ReturnFollowUpResult> SendFollowUpAsync(ReturnThread thread, CancellationToken cancellationToken = default)
    {
        if (thread is null)
        {
            throw new ArgumentNullException(nameof(thread));
        }

        var latest = thread.Latest;
        var account = _accountRouter.GetAccount(latest.AccountId);
        var provider = _accountRouter.ResolveProvider(latest.AccountId);

        var to = new MailAddress(latest.Sender.Address, latest.Sender.Name);
        var envelope = new MailEnvelope(new[] { to });

        var subject = $"[Follow-up] {thread.TrackingKey} - pendência de documentação";
        var reasons = latest.Classification.Reasons.Any()
            ? string.Join(", ", latest.Classification.Reasons)
            : latest.Status.ToString();
        var htmlBody = $"""
            <html>
              <body>
                <p>Olá,</p>
                <p>Identificamos pendências no protocolo <strong>{thread.TrackingKey}</strong> com status <strong>{latest.Status}</strong>.</p>
                <p>Por gentileza, responda este e-mail com as informações solicitadas para concluirmos a análise.</p>
                <p>Motivos da classificação: {reasons}.</p>
                <p>Atenciosamente,<br/>{account.DisplayName ?? account.Address}</p>
              </body>
            </html>
            """;

        var content = new MailContent(subject, htmlBody);
        var request = new MailSendRequest(account, envelope, content, thread.TrackingKey);

        var result = await provider.SendAsync(request, cancellationToken).ConfigureAwait(false);

        _logger?.LogInformation(
            "Follow-up enviado para {Recipient} com mensagem {MessageId}.",
            to.Email,
            result.MessageId);

        return new ReturnFollowUpResult(result.MessageId, result.ThreadId, result.SentAt);
    }
}
