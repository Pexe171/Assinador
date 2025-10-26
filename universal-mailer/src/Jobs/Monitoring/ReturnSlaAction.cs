using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Jobs.Monitoring;

/// <summary>
/// Representa uma ação realizada pelo monitoramento de SLA.
/// </summary>
public sealed record ReturnSlaAction
{
    private ReturnSlaAction(string trackingKey, ReturnSlaStatus? newStatus, bool followUpSent)
    {
        TrackingKey = trackingKey;
        NewStatus = newStatus;
        FollowUpSent = followUpSent;
    }

    public string TrackingKey { get; }

    public ReturnSlaStatus? NewStatus { get; }

    public bool FollowUpSent { get; }

    public static ReturnSlaAction StatusChanged(string trackingKey, ReturnSlaStatus status)
        => new(trackingKey, status, false);

    public static ReturnSlaAction FollowUp(string trackingKey)
        => new(trackingKey, null, true);
}
