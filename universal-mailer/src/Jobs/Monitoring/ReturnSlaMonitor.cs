using Microsoft.Extensions.Logging;
using UniversalMailer.Core.Returns.Contracts;
using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Jobs.Monitoring;

/// <summary>
/// Avalia pendências de retorno para marcar SLA e disparar follow-ups automáticos.
/// </summary>
public sealed class ReturnSlaMonitor
{
    private readonly IReturnStore _store;
    private readonly IReturnFollowUpDispatcher _followUpDispatcher;
    private readonly ReturnSlaOptions _options;
    private readonly ILogger<ReturnSlaMonitor>? _logger;

    public ReturnSlaMonitor(
        IReturnStore store,
        IReturnFollowUpDispatcher followUpDispatcher,
        ReturnSlaOptions options,
        ILogger<ReturnSlaMonitor>? logger = null)
    {
        _store = store ?? throw new ArgumentNullException(nameof(store));
        _followUpDispatcher = followUpDispatcher ?? throw new ArgumentNullException(nameof(followUpDispatcher));
        _options = options ?? throw new ArgumentNullException(nameof(options));
        _logger = logger;
    }

    public async Task<IReadOnlyList<ReturnSlaAction>> RunAsync(CancellationToken cancellationToken = default)
    {
        var now = DateTimeOffset.UtcNow;
        var actions = new List<ReturnSlaAction>();

        var threads = await _store.ListAsync(cancellationToken).ConfigureAwait(false);
        foreach (var thread in threads)
        {
            cancellationToken.ThrowIfCancellationRequested();

            if (!thread.HasValidTrackingId)
            {
                continue;
            }

            var latest = thread.Latest;
            if (IsResolved(latest.Status))
            {
                continue;
            }

            var elapsed = now - latest.ReceivedAt;
            var desiredStatus = DetermineSlaStatus(elapsed);

            if (desiredStatus != thread.SlaStatus)
            {
                await _store.UpdateSlaStatusAsync(thread.TrackingKey, desiredStatus, now, cancellationToken).ConfigureAwait(false);
                actions.Add(ReturnSlaAction.StatusChanged(thread.TrackingKey, desiredStatus));
                _logger?.LogInformation("SLA atualizado: {Tracking} => {Status}.", thread.TrackingKey, desiredStatus);
            }

            if (ShouldSendFollowUp(desiredStatus, thread.LastFollowUpAt, now))
            {
                var result = await _followUpDispatcher.SendFollowUpAsync(thread, cancellationToken).ConfigureAwait(false);
                await _store.UpdateFollowUpAsync(thread.TrackingKey, result.SentAt, cancellationToken).ConfigureAwait(false);
                actions.Add(ReturnSlaAction.FollowUp(thread.TrackingKey));
                _logger?.LogInformation("Follow-up disparado para {Tracking} (mensagem {MessageId}).", thread.TrackingKey, result.MessageId);
            }
        }

        return actions;
    }

    private ReturnSlaStatus DetermineSlaStatus(TimeSpan elapsed)
    {
        if (elapsed >= _options.OverdueAfter)
        {
            return ReturnSlaStatus.Vencido;
        }

        if (elapsed >= _options.AttentionAfter)
        {
            return ReturnSlaStatus.Atencao;
        }

        return ReturnSlaStatus.EmDia;
    }

    private bool ShouldSendFollowUp(ReturnSlaStatus status, DateTimeOffset? lastFollowUp, DateTimeOffset now)
    {
        if (status == ReturnSlaStatus.EmDia)
        {
            return false;
        }

        if (lastFollowUp is null)
        {
            return true;
        }

        return now - lastFollowUp.Value >= _options.FollowUpInterval;
    }

    private static bool IsResolved(ReturnStatus status)
        => status is ReturnStatus.Validado or ReturnStatus.Invalidado;
}
