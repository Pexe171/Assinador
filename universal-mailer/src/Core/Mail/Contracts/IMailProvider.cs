using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace UniversalMailer.Core.Mail.Contracts;

/// <summary>
/// Contrato universal para provedores de e-mail. Mantém o domínio isolado dos detalhes de integração.
/// </summary>
public interface IMailProvider
{
    Task<MailOperationResult> SendAsync(SendMessageRequest request, CancellationToken cancellationToken = default);

    Task<MailOperationResult> SaveDraftAsync(SaveDraftRequest request, CancellationToken cancellationToken = default);

    Task<MailMessage?> GetMessageAsync(GetMessageRequest request, CancellationToken cancellationToken = default);

    Task<IReadOnlyList<MailMessage>> ListInboxAsync(ListInboxRequest request, CancellationToken cancellationToken = default);

    Task<MailOperationResult> ReplyAllAsync(ReplyAllRequest request, CancellationToken cancellationToken = default);

    Task<MailTrackingInfo> TrackIdAsync(TrackMessageRequest request, CancellationToken cancellationToken = default);
}
