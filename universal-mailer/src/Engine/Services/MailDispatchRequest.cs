using System;
using System.Collections.Generic;
using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Engine.Services;

/// <summary>
/// Dados necessários para preparar a prévia e o envio efetivo.
/// </summary>
public sealed class MailDispatchRequest
{
    public MailDispatchRequest(
        MailAccount account,
        IReadOnlyCollection<MailAddress> to,
        IReadOnlyCollection<MailAddress>? cc,
        IReadOnlyCollection<MailAddress>? bcc,
        IReadOnlyDictionary<string, string> values,
        string templateKey)
    {
        Account = account ?? throw new ArgumentNullException(nameof(account));
        To = to ?? throw new ArgumentNullException(nameof(to));
        Cc = cc ?? Array.Empty<MailAddress>();
        Bcc = bcc ?? Array.Empty<MailAddress>();
        Values = values ?? throw new ArgumentNullException(nameof(values));
        TemplateKey = string.IsNullOrWhiteSpace(templateKey)
            ? throw new ArgumentException("A chave de template é obrigatória.", nameof(templateKey))
            : templateKey;
    }

    public MailAccount Account { get; }

    public IReadOnlyCollection<MailAddress> To { get; }

    public IReadOnlyCollection<MailAddress> Cc { get; }

    public IReadOnlyCollection<MailAddress> Bcc { get; }

    public IReadOnlyDictionary<string, string> Values { get; }

    public string TemplateKey { get; }
}
