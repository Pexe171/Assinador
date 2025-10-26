using UniversalMailer.Core.Mail.Records;

namespace UniversalMailer.Core.Mail.Contracts;

/// <summary>
/// Responsável por persistir os envios realizados para consultas futuras.
/// </summary>
public interface IMailDispatchStore
{
    Task SaveAsync(MailDispatchRecord record, CancellationToken cancellationToken = default);
}
