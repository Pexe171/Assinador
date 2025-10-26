using System.Collections.Concurrent;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Returns.Contracts;
using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Persistence.Stores;

/// <summary>
/// Armazena retornos em um arquivo JSON estruturado, mantendo histórico por protocolo.
/// </summary>
public sealed class FileReturnStore : IReturnStore
{
    private readonly string _filePath;
    private readonly JsonSerializerOptions _serializerOptions = new()
    {
        WriteIndented = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        Converters = { new JsonStringEnumConverter() }
    };

    private readonly SemaphoreSlim _mutex = new(1, 1);
    private readonly ConcurrentDictionary<string, ReturnThread> _threads = new(StringComparer.OrdinalIgnoreCase);
    private bool _initialized;

    public FileReturnStore(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
        {
            throw new ArgumentException("O caminho do arquivo é obrigatório.", nameof(filePath));
        }

        _filePath = filePath;
    }

    public async Task<ReturnThread?> GetAsync(string trackingKey, CancellationToken cancellationToken = default)
    {
        await EnsureInitializedAsync(cancellationToken).ConfigureAwait(false);
        return _threads.TryGetValue(trackingKey, out var thread) ? CloneThread(thread) : null;
    }

    public async Task<ReturnThread> SaveAsync(ReturnRecord record, CancellationToken cancellationToken = default)
    {
        if (record is null)
        {
            throw new ArgumentNullException(nameof(record));
        }

        await EnsureInitializedAsync(cancellationToken).ConfigureAwait(false);
        cancellationToken.ThrowIfCancellationRequested();

        await _mutex.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            ReturnThread updatedThread;
            if (_threads.TryGetValue(record.TrackingKey, out var existing))
            {
                var messages = existing.Messages.ToList();
                var index = messages.FindIndex(item => item.ProviderMessageId.Equals(record.ProviderMessageId, StringComparison.OrdinalIgnoreCase));
                if (index >= 0)
                {
                    messages[index] = record;
                }
                else
                {
                    messages.Add(record);
                }

                updatedThread = existing with
                {
                    HasValidTrackingId = existing.HasValidTrackingId || record.HasValidTrackingId,
                    Messages = messages.AsReadOnly(),
                    UpdatedAt = record.ReceivedAt > existing.UpdatedAt ? record.ReceivedAt : existing.UpdatedAt
                };
            }
            else
            {
                updatedThread = CreateThread(record);
            }

            _threads[record.TrackingKey] = updatedThread;

            await PersistAsync(cancellationToken).ConfigureAwait(false);

            return CloneThread(updatedThread);
        }
        finally
        {
            _mutex.Release();
        }
    }

    public async Task<IReadOnlyList<ReturnThread>> ListAsync(CancellationToken cancellationToken = default)
    {
        await EnsureInitializedAsync(cancellationToken).ConfigureAwait(false);
        return _threads.Values.Select(CloneThread).OrderBy(thread => thread.CreatedAt).ToList();
    }

    public async Task UpdateSlaStatusAsync(string trackingKey, ReturnSlaStatus status, DateTimeOffset changedAt, CancellationToken cancellationToken = default)
    {
        await EnsureInitializedAsync(cancellationToken).ConfigureAwait(false);
        cancellationToken.ThrowIfCancellationRequested();

        await _mutex.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            if (_threads.TryGetValue(trackingKey, out var thread))
            {
                var updated = thread with
                {
                    SlaStatus = status,
                    SlaStatusChangedAt = changedAt
                };

                _threads[trackingKey] = updated;
                await PersistAsync(cancellationToken).ConfigureAwait(false);
            }
        }
        finally
        {
            _mutex.Release();
        }
    }

    public async Task UpdateFollowUpAsync(string trackingKey, DateTimeOffset sentAt, CancellationToken cancellationToken = default)
    {
        await EnsureInitializedAsync(cancellationToken).ConfigureAwait(false);
        cancellationToken.ThrowIfCancellationRequested();

        await _mutex.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            if (_threads.TryGetValue(trackingKey, out var thread))
            {
                var updated = thread with { LastFollowUpAt = sentAt };
                _threads[trackingKey] = updated;
                await PersistAsync(cancellationToken).ConfigureAwait(false);
            }
        }
        finally
        {
            _mutex.Release();
        }
    }

    private async Task EnsureInitializedAsync(CancellationToken cancellationToken)
    {
        if (_initialized)
        {
            return;
        }

        await _mutex.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            if (_initialized)
            {
                return;
            }

            if (File.Exists(_filePath))
            {
                await using var stream = File.OpenRead(_filePath);
                var payload = await JsonSerializer.DeserializeAsync<PersistedPayload>(stream, _serializerOptions, cancellationToken).ConfigureAwait(false);
                if (payload?.Threads is not null)
                {
                    foreach (var persisted in payload.Threads)
                    {
                        var messages = persisted.Messages?.Select(Map).ToList() ?? new List<ReturnRecord>();
                        var thread = new ReturnThread(
                            persisted.TrackingKey,
                            persisted.HasValidTrackingId,
                            messages.AsReadOnly(),
                            persisted.SlaStatus,
                            persisted.SlaStatusChangedAt,
                            persisted.CreatedAt,
                            persisted.UpdatedAt,
                            persisted.LastFollowUpAt);
                        _threads[persisted.TrackingKey] = thread;
                    }
                }
            }

            _initialized = true;
        }
        finally
        {
            _mutex.Release();
        }
    }

    private async Task PersistAsync(CancellationToken cancellationToken)
    {
        var directory = Path.GetDirectoryName(_filePath);
        if (!string.IsNullOrWhiteSpace(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var payload = new PersistedPayload
        {
            Threads = _threads.Values
                .OrderBy(thread => thread.CreatedAt)
                .Select(ToPersisted)
                .ToList()
        };

        await using var stream = new FileStream(_filePath, FileMode.Create, FileAccess.Write, FileShare.Read);
        await JsonSerializer.SerializeAsync(stream, payload, _serializerOptions, cancellationToken).ConfigureAwait(false);
    }

    private static ReturnThread CloneThread(ReturnThread thread)
    {
        var messages = thread.Messages.Select(CloneRecord).ToList().AsReadOnly();
        return thread with { Messages = messages };
    }

    private static ReturnRecord CloneRecord(ReturnRecord record)
        => record with
        {
            Metadata = record.Metadata is null
                ? null
                : new Dictionary<string, string>(record.Metadata, StringComparer.OrdinalIgnoreCase)
        };

    private static ReturnThread CreateThread(ReturnRecord record)
    {
        return new ReturnThread(
            record.TrackingKey,
            record.HasValidTrackingId,
            new List<ReturnRecord> { record }.AsReadOnly(),
            ReturnSlaStatus.EmDia,
            record.ReceivedAt,
            record.ReceivedAt,
            record.ReceivedAt,
            null);
    }

    private static PersistedThread ToPersisted(ReturnThread thread)
    {
        return new PersistedThread
        {
            TrackingKey = thread.TrackingKey,
            HasValidTrackingId = thread.HasValidTrackingId,
            SlaStatus = thread.SlaStatus,
            SlaStatusChangedAt = thread.SlaStatusChangedAt,
            CreatedAt = thread.CreatedAt,
            UpdatedAt = thread.UpdatedAt,
            LastFollowUpAt = thread.LastFollowUpAt,
            Messages = thread.Messages.Select(ToPersisted).ToList()
        };
    }

    private static PersistedReturnRecord ToPersisted(ReturnRecord record)
    {
        return new PersistedReturnRecord
        {
            TrackingKey = record.TrackingKey,
            HasValidTrackingId = record.HasValidTrackingId,
            ProviderMessageId = record.ProviderMessageId,
            AccountId = record.AccountId,
            ProviderType = record.ProviderType,
            Sender = new PersistedParticipant
            {
                Address = record.Sender.Address,
                Name = record.Sender.Name
            },
            Subject = record.Subject,
            BodyPreview = record.BodyPreview,
            Classification = new PersistedClassification
            {
                Status = record.Classification.Status,
                Score = record.Classification.Score,
                MatchedKeywords = record.Classification.MatchedKeywords.ToArray(),
                Reasons = record.Classification.Reasons.ToArray(),
                RequiresManualReview = record.Classification.RequiresManualReview
            },
            ReceivedAt = record.ReceivedAt,
            ConversationId = record.ConversationId,
            Metadata = record.Metadata is null
                ? null
                : new Dictionary<string, string>(record.Metadata, StringComparer.OrdinalIgnoreCase)
        };
    }

    private static ReturnRecord Map(PersistedReturnRecord record)
    {
        return new ReturnRecord(
            record.TrackingKey,
            record.HasValidTrackingId,
            record.ProviderMessageId,
            record.AccountId,
            record.ProviderType,
            new MailParticipant(record.Sender.Address, record.Sender.Name),
            record.Subject,
            record.BodyPreview,
            new ReturnClassification(
                record.Classification.Status,
                record.Classification.Score,
                record.Classification.MatchedKeywords ?? Array.Empty<string>(),
                record.Classification.Reasons ?? Array.Empty<string>(),
                record.Classification.RequiresManualReview),
            record.ReceivedAt,
            record.ConversationId,
            record.Metadata);
    }

    private sealed class PersistedPayload
    {
        public List<PersistedThread>? Threads { get; set; }
    }

    private sealed class PersistedThread
    {
        public string TrackingKey { get; set; } = string.Empty;

        public bool HasValidTrackingId { get; set; }

        public ReturnSlaStatus SlaStatus { get; set; }

        public DateTimeOffset SlaStatusChangedAt { get; set; }

        public DateTimeOffset CreatedAt { get; set; }

        public DateTimeOffset UpdatedAt { get; set; }

        public DateTimeOffset? LastFollowUpAt { get; set; }

        public List<PersistedReturnRecord> Messages { get; set; } = new();
    }

    private sealed class PersistedReturnRecord
    {
        public string TrackingKey { get; set; } = string.Empty;

        public bool HasValidTrackingId { get; set; }

        public string ProviderMessageId { get; set; } = string.Empty;

        public string AccountId { get; set; } = string.Empty;

        public MailProviderType ProviderType { get; set; }

        public PersistedParticipant Sender { get; set; } = new();

        public string Subject { get; set; } = string.Empty;

        public string BodyPreview { get; set; } = string.Empty;

        public PersistedClassification Classification { get; set; } = new();

        public DateTimeOffset ReceivedAt { get; set; }

        public string? ConversationId { get; set; }

        public Dictionary<string, string>? Metadata { get; set; }
    }

    private sealed class PersistedParticipant
    {
        public string Address { get; set; } = string.Empty;

        public string? Name { get; set; }
    }

    private sealed class PersistedClassification
    {
        public ReturnStatus Status { get; set; }

        public double Score { get; set; }

        public string[]? MatchedKeywords { get; set; }

        public string[]? Reasons { get; set; }

        public bool RequiresManualReview { get; set; }
    }
}
