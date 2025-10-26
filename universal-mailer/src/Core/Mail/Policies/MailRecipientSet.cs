using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Core.Mail.Policies;

/// <summary>
/// Representa coleções saneadas de destinatários.
/// </summary>
public sealed record MailRecipientSet(
    IReadOnlyCollection<MailAddress> To,
    IReadOnlyCollection<MailAddress> Cc,
    IReadOnlyCollection<MailAddress> Bcc);
