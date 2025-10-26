using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Mail.Adapters.SmtpImapAdapter;

/// <summary>
/// Contrato para abstrair a integração com bibliotecas SMTP/IMAP (ex.: MailKit).
/// </summary>
public interface ISmtpImapClient
{
    Task<MailOperationResult> SendAsync(SendMessageRequest request, CancellationToken cancellationToken);

    Task<MailOperationResult> SaveDraftAsync(SaveDraftRequest request, CancellationToken cancellationToken);

    Task<MailMessage?> GetMessageAsync(GetMessageRequest request, CancellationToken cancellationToken);

    Task<IReadOnlyList<MailMessage>> ListInboxAsync(ListInboxRequest request, CancellationToken cancellationToken);

    Task<MailOperationResult> ReplyAllAsync(ReplyAllRequest request, CancellationToken cancellationToken);

    Task<MailTrackingInfo> TrackByHeadersAsync(TrackMessageRequest request, CancellationToken cancellationToken);
}
