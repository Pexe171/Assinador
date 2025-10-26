using System;
using System.Threading;
using System.Threading.Tasks;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Mail.Adapters.SmtpImapAdapter;

/// <summary>
/// Stub temporário para o adapter SMTP/IMAP enquanto as integrações
/// completas não estão disponíveis.
/// </summary>
public sealed class SmtpImapMailProvider : IMailProvider
{
    private const string NotSupportedMessage = "O adapter SMTP/IMAP ainda não foi migrado.";

    public Task<MailSendResult> SendAsync(MailSendRequest request, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        throw new NotSupportedException(NotSupportedMessage);
    }
}
