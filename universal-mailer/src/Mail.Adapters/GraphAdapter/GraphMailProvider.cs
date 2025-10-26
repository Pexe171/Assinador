using System;
using System.Threading;
using System.Threading.Tasks;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Mail.Adapters.GraphAdapter;

/// <summary>
/// Placeholder para o adapter de Microsoft Graph enquanto a nova infraestrutura
/// de envio não está disponível.
/// </summary>
public sealed class GraphMailProvider : IMailProvider
{
    private const string NotSupportedMessage = "O adapter do Microsoft Graph ainda não foi migrado.";

    public Task<MailSendResult> SendAsync(MailSendRequest request, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        throw new NotSupportedException(NotSupportedMessage);
    }
}
