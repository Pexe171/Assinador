namespace UniversalMailer.Jobs.Monitoring;

/// <summary>
/// Define prazos para classificação de SLA e follow-ups automáticos.
/// </summary>
public sealed record ReturnSlaOptions
{
    public TimeSpan AttentionAfter { get; init; } = TimeSpan.FromHours(12);

    public TimeSpan OverdueAfter { get; init; } = TimeSpan.FromHours(24);

    public TimeSpan FollowUpInterval { get; init; } = TimeSpan.FromHours(24);
}
