using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Core.Mail.Policies;

/// <summary>
/// Define regras para sanitização de destinatários antes do envio.
/// </summary>
public interface IMailRecipientPolicy
{
    MailRecipientSet Apply(
        IEnumerable<MailAddress> to,
        IEnumerable<MailAddress>? cc,
        IEnumerable<MailAddress>? bcc);
}
