using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Core.Returns.Contracts;

/// <summary>
/// Define operações de persistência para retornos processados.
/// </summary>
public interface IReturnStore
{
    Task<ReturnThread?> GetAsync(string trackingKey, CancellationToken cancellationToken = default);

    Task<ReturnThread> SaveAsync(ReturnRecord record, CancellationToken cancellationToken = default);

    Task<IReadOnlyList<ReturnThread>> ListAsync(CancellationToken cancellationToken = default);

    Task UpdateSlaStatusAsync(string trackingKey, ReturnSlaStatus status, DateTimeOffset changedAt, CancellationToken cancellationToken = default);

    Task UpdateFollowUpAsync(string trackingKey, DateTimeOffset sentAt, CancellationToken cancellationToken = default);
}
