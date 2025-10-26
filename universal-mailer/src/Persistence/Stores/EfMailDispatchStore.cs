using Microsoft.EntityFrameworkCore;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Core.Mail.Records;
using UniversalMailer.Persistence.Db;
using UniversalMailer.Persistence.Entities;

namespace UniversalMailer.Persistence.Stores;

/// <summary>
/// Persiste os envios no banco relacional utilizando EF Core.
/// </summary>
public sealed class EfMailDispatchStore : IMailDispatchStore
{
    private readonly MailerDbContext _context;

    public EfMailDispatchStore(MailerDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task SaveAsync(MailDispatchRecord record, CancellationToken cancellationToken = default)
    {
        if (record is null)
        {
            throw new ArgumentNullException(nameof(record));
        }

        cancellationToken.ThrowIfCancellationRequested();

        var existing = await _context.MailDispatches
            .Include(entity => entity.Recipients)
            .FirstOrDefaultAsync(entity => entity.TrackingId == record.TrackingId, cancellationToken)
            .ConfigureAwait(false);

        if (existing is null)
        {
            var dispatch = CreateEntity(record);
            await _context.MailDispatches.AddAsync(dispatch, cancellationToken).ConfigureAwait(false);
        }
        else
        {
            UpdateEntity(existing, record);
        }

        await _context.SaveChangesAsync(cancellationToken).ConfigureAwait(false);
    }

    private static MailDispatchEntity CreateEntity(MailDispatchRecord record)
    {
        var entity = new MailDispatchEntity
        {
            Id = Guid.NewGuid(),
            TrackingId = record.TrackingId,
            TemplateKey = record.TemplateKey,
            TemplateVersion = record.TemplateVersion,
            AccountId = record.Account.Id,
            AccountName = record.Account.DisplayName,
            ProviderMessageId = record.Result.MessageId,
            ProviderThreadId = record.Result.ThreadId,
            SentAt = record.Result.SentAt,
            LoggedAt = record.CreatedAt,
            Recipients = new List<MailRecipientEntity>()
        };

        AppendRecipients(entity.Recipients, record.Envelope.To, MailRecipientType.To, entity.Id);
        AppendRecipients(entity.Recipients, record.Envelope.Cc, MailRecipientType.Cc, entity.Id);
        AppendRecipients(entity.Recipients, record.Envelope.Bcc, MailRecipientType.Bcc, entity.Id);

        return entity;
    }

    private static void UpdateEntity(MailDispatchEntity entity, MailDispatchRecord record)
    {
        entity.TemplateKey = record.TemplateKey;
        entity.TemplateVersion = record.TemplateVersion;
        entity.AccountId = record.Account.Id;
        entity.AccountName = record.Account.DisplayName;
        entity.ProviderMessageId = record.Result.MessageId;
        entity.ProviderThreadId = record.Result.ThreadId;
        entity.SentAt = record.Result.SentAt;
        entity.LoggedAt = record.CreatedAt;

        entity.Recipients.Clear();
        AppendRecipients(entity.Recipients, record.Envelope.To, MailRecipientType.To, entity.Id);
        AppendRecipients(entity.Recipients, record.Envelope.Cc, MailRecipientType.Cc, entity.Id);
        AppendRecipients(entity.Recipients, record.Envelope.Bcc, MailRecipientType.Bcc, entity.Id);
    }

    private static void AppendRecipients(ICollection<MailRecipientEntity> target, IEnumerable<MailAddress> addresses, MailRecipientType type, Guid dispatchId)
    {
        foreach (var address in addresses)
        {
            target.Add(new MailRecipientEntity
            {
                Id = Guid.NewGuid(),
                DispatchId = dispatchId,
                Type = type,
                Email = address.Email,
                Name = address.Name
            });
        }
    }
}
