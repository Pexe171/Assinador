using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Core.Mail.Contracts;

/// <summary>
/// Contrato padrão para os adapters de envio.
/// </summary>
public interface IMailProvider
{
    Task<MailSendResult> SendAsync(MailSendRequest request, CancellationToken cancellationToken = default);
}
