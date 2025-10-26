using System;
using System.Collections.Generic;
using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Persistence.Entities;

public sealed class MailProviderEntity
{
    public Guid Id { get; set; }

    public string Name { get; set; } = string.Empty;

    public string DisplayName { get; set; } = string.Empty;

    public MailProviderType Type { get; set; }

    public string SettingsJson { get; set; } = "{}";

    public bool IsActive { get; set; } = true;

    public DateTimeOffset CreatedAt { get; set; }

    public DateTimeOffset UpdatedAt { get; set; }

    public ICollection<MailAccountEntity> Accounts { get; set; } = new List<MailAccountEntity>();
}

public sealed class MailAccountEntity
{
    public Guid Id { get; set; }

    public string AccountId { get; set; } = string.Empty;

    public string Address { get; set; } = string.Empty;

    public string? DisplayName { get; set; }

    public string MetadataJson { get; set; } = "{}";

    public bool IsActive { get; set; } = true;

    public Guid ProviderId { get; set; }

    public MailProviderEntity Provider { get; set; } = null!;

    public DateTimeOffset CreatedAt { get; set; }

    public DateTimeOffset UpdatedAt { get; set; }
}
