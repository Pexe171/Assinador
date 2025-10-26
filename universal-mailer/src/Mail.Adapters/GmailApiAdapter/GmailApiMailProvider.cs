using System;
using System.Threading;
using System.Threading.Tasks;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Mail.Adapters.GmailApiAdapter;

/// <summary>
/// Adapter da Gmail API ainda não migrado para a nova pilha de envio.
/// Por enquanto, mantemos a classe apenas para sinalizar que o recurso
/// não está disponível nesta distribuição.
/// </summary>
public sealed class GmailApiMailProvider : IMailProvider
{
    private const string NotSupportedMessage = "O adapter da Gmail API ainda não está disponível nesta versão.";

    public Task<MailSendResult> SendAsync(MailSendRequest request, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        throw new NotSupportedException(NotSupportedMessage);
    }
}
