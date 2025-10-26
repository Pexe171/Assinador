using System;
using System.Collections.Generic;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Persistence.Entities;

public sealed class ReturnThreadEntity
{
    public Guid Id { get; set; }

    public string TrackingKey { get; set; } = string.Empty;

    public bool HasValidTrackingId { get; set; }

    public ReturnSlaStatus SlaStatus { get; set; }

    public DateTimeOffset SlaStatusChangedAt { get; set; }

    public DateTimeOffset CreatedAt { get; set; }

    public DateTimeOffset UpdatedAt { get; set; }

    public DateTimeOffset? LastFollowUpAt { get; set; }

    public ICollection<ReturnMessageEntity> Messages { get; set; } = new List<ReturnMessageEntity>();
}

public sealed class ReturnMessageEntity
{
    public Guid Id { get; set; }

    public Guid ThreadId { get; set; }

    public ReturnThreadEntity Thread { get; set; } = null!;

    public string ProviderMessageId { get; set; } = string.Empty;

    public string AccountId { get; set; } = string.Empty;

    public MailProviderType ProviderType { get; set; }

    public string SenderAddress { get; set; } = string.Empty;

    public string? SenderName { get; set; }

    public string Subject { get; set; } = string.Empty;

    public string BodyPreview { get; set; } = string.Empty;

    public ReturnStatus Status { get; set; }

    public double Score { get; set; }

    public string MatchedKeywordsJson { get; set; } = "[]";

    public string ReasonsJson { get; set; } = "[]";

    public bool RequiresManualReview { get; set; }

    public DateTimeOffset ReceivedAt { get; set; }

    public string? ConversationId { get; set; }

    public string MetadataJson { get; set; } = "{}";
}
