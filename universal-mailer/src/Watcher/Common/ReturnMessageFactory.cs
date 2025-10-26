using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Core.Returns.Processing;

namespace UniversalMailer.Watcher.Common;

/// <summary>
/// Converte mensagens genéricas dos adapters em registros prontos para processamento.
/// </summary>
public static class ReturnMessageFactory
{
    public static ReturnMessage FromMailMessage(MailAccount account, MailMessage message)
    {
        if (account is null)
        {
            throw new ArgumentNullException(nameof(account));
        }

        if (message is null)
        {
            throw new ArgumentNullException(nameof(message));
        }

        var subject = ReturnTextSanitizer.Normalize(message.Envelope.Subject);
        var bodySource = !string.IsNullOrWhiteSpace(message.Body.Text)
            ? message.Body.Text
            : message.Body.Html;
        var body = ReturnTextSanitizer.Normalize(bodySource);

        return new ReturnMessage(
            message.ProviderMessageId,
            account.AccountId,
            account.Provider.Type,
            message.Envelope.From,
            subject,
            body,
            message.CreatedAt,
            message.ThreadId,
            message.Headers);
    }
}
