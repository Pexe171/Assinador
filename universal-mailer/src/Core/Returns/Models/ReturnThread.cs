namespace UniversalMailer.Core.Returns.Models;

/// <summary>
/// Consolida todos os retornos vinculados a um mesmo identificador de rastreamento.
/// </summary>
public sealed record ReturnThread(
    string TrackingKey,
    bool HasValidTrackingId,
    IReadOnlyList<ReturnRecord> Messages,
    ReturnSlaStatus SlaStatus,
    DateTimeOffset SlaStatusChangedAt,
    DateTimeOffset CreatedAt,
    DateTimeOffset UpdatedAt,
    DateTimeOffset? LastFollowUpAt)
{
    public ReturnRecord Latest => Messages[^1];
}
