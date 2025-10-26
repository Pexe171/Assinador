using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Core.Mail.Records;

namespace UniversalMailer.Engine.Services;

/// <summary>
/// Resultado completo após envio e persistência.
/// </summary>
public sealed class MailDispatchOutcome
{
    public MailDispatchOutcome(MailSendResult providerResult, MailDispatchRecord record)
    {
        ProviderResult = providerResult;
        Record = record;
    }

    public MailSendResult ProviderResult { get; }

    public MailDispatchRecord Record { get; }
}
