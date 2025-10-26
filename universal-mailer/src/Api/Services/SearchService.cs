using Microsoft.EntityFrameworkCore;
using UniversalMailer.Api.Contracts.Search;
using UniversalMailer.Persistence.Db;
using UniversalMailer.Persistence.Entities;

namespace UniversalMailer.Api.Services;

public sealed class SearchService
{
    private readonly MailerDbContext _context;

    public SearchService(MailerDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<SearchResponse> SearchAsync(string? protocolo, string? email, string? status, CancellationToken cancellationToken)
    {
        var emailResults = await BuildEmailQuery(protocolo, email)
            .OrderByDescending(dispatch => dispatch.SentAt)
            .Take(50)
            .ToListAsync(cancellationToken)
            .ConfigureAwait(false);

        var retornoResults = await BuildReturnQuery(protocolo, email, status)
            .OrderByDescending(thread => thread.UpdatedAt)
            .Take(50)
            .ToListAsync(cancellationToken)
            .ConfigureAwait(false);

        var envios = emailResults.Select(dispatch => new EmailSummaryResponse(
            dispatch.TrackingId,
            dispatch.TemplateKey,
            dispatch.AccountName,
            dispatch.SentAt,
            dispatch.Recipients.Select(recipient => recipient.Email).ToArray(),
            dispatch.ProviderMessageId)).ToList();

        var retornos = retornoResults.Select(thread =>
        {
            var latest = thread.Messages.OrderBy(message => message.ReceivedAt).Last();
            return new ReturnSummaryResponse(
                thread.TrackingKey,
                latest.Status.ToString(),
                latest.ReceivedAt,
                latest.Subject,
                latest.AccountId);
        }).ToList();

        return new SearchResponse(envios, retornos);
    }

    private IQueryable<MailDispatchEntity> BuildEmailQuery(string? protocolo, string? email)
    {
        var query = _context.MailDispatches
            .AsNoTracking()
            .Include(dispatch => dispatch.Recipients)
            .AsQueryable();

        if (!string.IsNullOrWhiteSpace(protocolo))
        {
            query = query.Where(dispatch => dispatch.TrackingId.Contains(protocolo));
        }

        if (!string.IsNullOrWhiteSpace(email))
        {
            query = query.Where(dispatch => dispatch.Recipients.Any(recipient => recipient.Email.Contains(email)));
        }

        return query;
    }

    private IQueryable<ReturnThreadEntity> BuildReturnQuery(string? protocolo, string? email, string? status)
    {
        var query = _context.ReturnThreads
            .AsNoTracking()
            .Include(thread => thread.Messages)
            .AsQueryable();

        if (!string.IsNullOrWhiteSpace(protocolo))
        {
            query = query.Where(thread => thread.TrackingKey.Contains(protocolo));
        }

        if (!string.IsNullOrWhiteSpace(email))
        {
            query = query.Where(thread => thread.Messages.Any(message => message.SenderAddress.Contains(email)));
        }

        if (!string.IsNullOrWhiteSpace(status) && Enum.TryParse(status, true, out Core.Returns.Models.ReturnStatus parsed))
        {
            query = query.Where(thread => thread.Messages.Any(message => message.Status == parsed));
        }

        return query;
    }
}
