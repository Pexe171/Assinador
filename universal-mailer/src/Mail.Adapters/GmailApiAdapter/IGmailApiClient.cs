using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Mail.Adapters.GmailApiAdapter;

/// <summary>
/// Interface que encapsula chamadas à API nativa do Gmail.
/// </summary>
public interface IGmailApiClient
{
    Task<MailOperationResult> SendAsync(SendMessageRequest request, CancellationToken cancellationToken);

    Task<MailOperationResult> SaveDraftAsync(SaveDraftRequest request, CancellationToken cancellationToken);

    Task<MailMessage?> GetMessageAsync(GetMessageRequest request, CancellationToken cancellationToken);

    Task<IReadOnlyList<MailMessage>> ListInboxAsync(ListInboxRequest request, CancellationToken cancellationToken);

    Task<MailOperationResult> ReplyAllAsync(ReplyAllRequest request, CancellationToken cancellationToken);

    Task<MailTrackingInfo> TrackIdAsync(TrackMessageRequest request, CancellationToken cancellationToken);
}
