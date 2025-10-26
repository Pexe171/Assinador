using System;

namespace UniversalMailer.Persistence.Entities;

public sealed class TemplateEntity
{
    public Guid Id { get; set; }

    public string Key { get; set; } = string.Empty;

    public string DisplayName { get; set; } = string.Empty;

    public string Version { get; set; } = "1.0.0";

    public string Subject { get; set; } = string.Empty;

    public string Body { get; set; } = string.Empty;

    public string? Description { get; set; }

    public bool IsActive { get; set; } = true;

    public DateTimeOffset CreatedAt { get; set; }

    public DateTimeOffset UpdatedAt { get; set; }
}
