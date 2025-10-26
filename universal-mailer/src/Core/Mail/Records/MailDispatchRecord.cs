using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Core.Mail.Records;

/// <summary>
/// Registro persistido após o envio, preservando metadados para auditoria.
/// </summary>
public sealed record MailDispatchRecord(
    string TrackingId,
    string TemplateKey,
    string TemplateVersion,
    MailAccount Account,
    MailEnvelope Envelope,
    MailSendResult Result,
    DateTimeOffset CreatedAt);
