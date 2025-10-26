using System;
using System.Collections.Generic;

namespace UniversalMailer.Persistence.Entities;

public sealed class MailDispatchEntity
{
    public Guid Id { get; set; }

    public string TrackingId { get; set; } = string.Empty;

    public string TemplateKey { get; set; } = string.Empty;

    public string TemplateVersion { get; set; } = string.Empty;

    public string AccountId { get; set; } = string.Empty;

    public string AccountName { get; set; } = string.Empty;

    public string ProviderMessageId { get; set; } = string.Empty;

    public string? ProviderThreadId { get; set; }

    public DateTimeOffset SentAt { get; set; }

    public DateTimeOffset LoggedAt { get; set; }

    public ICollection<MailRecipientEntity> Recipients { get; set; } = new List<MailRecipientEntity>();
}

public sealed class MailRecipientEntity
{
    public Guid Id { get; set; }

    public Guid DispatchId { get; set; }

    public MailDispatchEntity Dispatch { get; set; } = null!;

    public MailRecipientType Type { get; set; }

    public string Email { get; set; } = string.Empty;

    public string? Name { get; set; }
}

public enum MailRecipientType
{
    To,
    Cc,
    Bcc
}
