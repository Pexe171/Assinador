using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Mail.Adapters.GraphAdapter;

/// <summary>
/// Contrato mínimo para encapsular operações do Microsoft Graph utilizadas pelo adapter.
/// Implementações reais delegarão para <see cref="Microsoft.Graph.GraphServiceClient"/>.
/// </summary>
public interface IGraphMailClient
{
    Task<MailOperationResult> SendAsync(SendMessageRequest request, CancellationToken cancellationToken);

    Task<MailOperationResult> SaveDraftAsync(SaveDraftRequest request, CancellationToken cancellationToken);

    Task<MailMessage?> GetMessageAsync(GetMessageRequest request, CancellationToken cancellationToken);

    Task<IReadOnlyList<MailMessage>> ListInboxAsync(ListInboxRequest request, CancellationToken cancellationToken);

    Task<MailOperationResult> ReplyAllAsync(ReplyAllRequest request, CancellationToken cancellationToken);

    Task<MailTrackingInfo> TrackIdAsync(TrackMessageRequest request, CancellationToken cancellationToken);
}
