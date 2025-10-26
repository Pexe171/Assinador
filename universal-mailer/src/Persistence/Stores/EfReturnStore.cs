using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Returns.Contracts;
using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Persistence.Db;
using UniversalMailer.Persistence.Entities;

namespace UniversalMailer.Persistence.Stores;

/// <summary>
/// Implementação de <see cref="IReturnStore"/> utilizando o banco relacional.
/// </summary>
public sealed class EfReturnStore : IReturnStore
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false
    };

    private readonly MailerDbContext _context;

    public EfReturnStore(MailerDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<ReturnThread?> GetAsync(string trackingKey, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(trackingKey))
        {
            throw new ArgumentException("O protocolo é obrigatório.", nameof(trackingKey));
        }

        var entity = await _context.ReturnThreads
            .AsNoTracking()
            .Include(thread => thread.Messages)
            .FirstOrDefaultAsync(thread => thread.TrackingKey == trackingKey, cancellationToken)
            .ConfigureAwait(false);

        return entity is null ? null : MapThread(entity);
    }

    public async Task<ReturnThread> SaveAsync(ReturnRecord record, CancellationToken cancellationToken = default)
    {
        if (record is null)
        {
            throw new ArgumentNullException(nameof(record));
        }

        cancellationToken.ThrowIfCancellationRequested();

        var thread = await _context.ReturnThreads
            .Include(entity => entity.Messages)
            .FirstOrDefaultAsync(entity => entity.TrackingKey == record.TrackingKey, cancellationToken)
            .ConfigureAwait(false);

        if (thread is null)
        {
            thread = CreateThread(record);
            await _context.ReturnThreads.AddAsync(thread, cancellationToken).ConfigureAwait(false);
        }
        else
        {
            ApplyRecord(thread, record);
        }

        await _context.SaveChangesAsync(cancellationToken).ConfigureAwait(false);

        var persisted = await _context.ReturnThreads
            .AsNoTracking()
            .Include(entity => entity.Messages)
            .FirstAsync(entity => entity.TrackingKey == record.TrackingKey, cancellationToken)
            .ConfigureAwait(false);

        return MapThread(persisted);
    }

    public async Task<IReadOnlyList<ReturnThread>> ListAsync(CancellationToken cancellationToken = default)
    {
        var threads = await _context.ReturnThreads
            .AsNoTracking()
            .Include(entity => entity.Messages)
            .OrderBy(entity => entity.CreatedAt)
            .ToListAsync(cancellationToken)
            .ConfigureAwait(false);

        return threads.Select(MapThread).ToList();
    }

    public async Task UpdateSlaStatusAsync(string trackingKey, ReturnSlaStatus status, DateTimeOffset changedAt, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(trackingKey))
        {
            throw new ArgumentException("O protocolo é obrigatório.", nameof(trackingKey));
        }

        var thread = await _context.ReturnThreads
            .FirstOrDefaultAsync(entity => entity.TrackingKey == trackingKey, cancellationToken)
            .ConfigureAwait(false);

        if (thread is null)
        {
            return;
        }

        thread.SlaStatus = status;
        thread.SlaStatusChangedAt = changedAt;
        await _context.SaveChangesAsync(cancellationToken).ConfigureAwait(false);
    }

    public async Task UpdateFollowUpAsync(string trackingKey, DateTimeOffset sentAt, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(trackingKey))
        {
            throw new ArgumentException("O protocolo é obrigatório.", nameof(trackingKey));
        }

        var thread = await _context.ReturnThreads
            .FirstOrDefaultAsync(entity => entity.TrackingKey == trackingKey, cancellationToken)
            .ConfigureAwait(false);

        if (thread is null)
        {
            return;
        }

        thread.LastFollowUpAt = sentAt;
        await _context.SaveChangesAsync(cancellationToken).ConfigureAwait(false);
    }

    private static ReturnThread MapThread(ReturnThreadEntity entity)
    {
        var messages = entity.Messages
            .OrderBy(message => message.ReceivedAt)
            .Select(message => MapRecord(entity, message))
            .ToList();

        return new ReturnThread(
            entity.TrackingKey,
            entity.HasValidTrackingId,
            messages,
            entity.SlaStatus,
            entity.SlaStatusChangedAt,
            entity.CreatedAt,
            entity.UpdatedAt,
            entity.LastFollowUpAt);
    }

    private static ReturnRecord MapRecord(ReturnThreadEntity thread, ReturnMessageEntity entity)
    {
        var sender = new MailParticipant(entity.SenderAddress, entity.SenderName);
        var classification = new ReturnClassification(
            entity.Status,
            entity.Score,
            DeserializeCollection(entity.MatchedKeywordsJson),
            DeserializeCollection(entity.ReasonsJson),
            entity.RequiresManualReview);

        var metadata = DeserializeDictionary(entity.MetadataJson);

        return new ReturnRecord(
            thread.TrackingKey,
            thread.HasValidTrackingId,
            entity.ProviderMessageId,
            entity.AccountId,
            entity.ProviderType,
            sender,
            entity.Subject,
            entity.BodyPreview,
            classification,
            entity.ReceivedAt,
            entity.ConversationId,
            metadata);
    }

    private static ReturnThreadEntity CreateThread(ReturnRecord record)
    {
        var threadId = Guid.NewGuid();
        var thread = new ReturnThreadEntity
        {
            Id = threadId,
            TrackingKey = record.TrackingKey,
            HasValidTrackingId = record.HasValidTrackingId,
            SlaStatus = ReturnSlaStatus.EmDia,
            SlaStatusChangedAt = record.ReceivedAt,
            CreatedAt = record.ReceivedAt,
            UpdatedAt = record.ReceivedAt,
            Messages = new List<ReturnMessageEntity>()
        };

        thread.Messages.Add(CreateMessage(thread, record));
        return thread;
    }

    private static void ApplyRecord(ReturnThreadEntity thread, ReturnRecord record)
    {
        thread.HasValidTrackingId |= record.HasValidTrackingId;
        thread.UpdatedAt = record.ReceivedAt > thread.UpdatedAt ? record.ReceivedAt : thread.UpdatedAt;

        var existing = thread.Messages
            .FirstOrDefault(message => message.ProviderMessageId.Equals(record.ProviderMessageId, StringComparison.OrdinalIgnoreCase));

        if (existing is null)
        {
            thread.Messages.Add(CreateMessage(thread, record));
            return;
        }

        UpdateMessage(existing, record);
    }

    private static ReturnMessageEntity CreateMessage(ReturnThreadEntity thread, ReturnRecord record)
    {
        return new ReturnMessageEntity
        {
            Id = Guid.NewGuid(),
            ThreadId = thread.Id,
            Thread = thread,
            ProviderMessageId = record.ProviderMessageId,
            AccountId = record.AccountId,
            ProviderType = record.ProviderType,
            SenderAddress = record.Sender.Address,
            SenderName = record.Sender.Name,
            Subject = record.Subject,
            BodyPreview = record.BodyPreview,
            Status = record.Status,
            Score = record.Classification.Score,
            MatchedKeywordsJson = SerializeCollection(record.Classification.MatchedKeywords),
            ReasonsJson = SerializeCollection(record.Classification.Reasons),
            RequiresManualReview = record.Classification.RequiresManualReview,
            ReceivedAt = record.ReceivedAt,
            ConversationId = record.ConversationId,
            MetadataJson = SerializeDictionary(record.Metadata)
        };
    }

    private static void UpdateMessage(ReturnMessageEntity entity, ReturnRecord record)
    {
        entity.AccountId = record.AccountId;
        entity.ProviderType = record.ProviderType;
        entity.SenderAddress = record.Sender.Address;
        entity.SenderName = record.Sender.Name;
        entity.Subject = record.Subject;
        entity.BodyPreview = record.BodyPreview;
        entity.Status = record.Status;
        entity.Score = record.Classification.Score;
        entity.MatchedKeywordsJson = SerializeCollection(record.Classification.MatchedKeywords);
        entity.ReasonsJson = SerializeCollection(record.Classification.Reasons);
        entity.RequiresManualReview = record.Classification.RequiresManualReview;
        entity.ReceivedAt = record.ReceivedAt;
        entity.ConversationId = record.ConversationId;
        entity.MetadataJson = SerializeDictionary(record.Metadata);
    }

    private static string SerializeCollection(IEnumerable<string> values)
        => JsonSerializer.Serialize(values ?? Array.Empty<string>(), JsonOptions);

    private static IReadOnlyCollection<string> DeserializeCollection(string json)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return Array.Empty<string>();
        }

        return JsonSerializer.Deserialize<string[]>(json, JsonOptions) ?? Array.Empty<string>();
    }

    private static string SerializeDictionary(IReadOnlyDictionary<string, string>? values)
        => JsonSerializer.Serialize(values ?? new Dictionary<string, string>(), JsonOptions);

    private static IReadOnlyDictionary<string, string>? DeserializeDictionary(string json)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return new Dictionary<string, string>();
        }

        return JsonSerializer.Deserialize<Dictionary<string, string>>(json, JsonOptions) ?? new Dictionary<string, string>();
    }
}
