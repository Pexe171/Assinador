using System.Linq;
using System.Text;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Mail.Adapters.FileSystem;

/// <summary>
/// Provider que grava os envios em disco, simulando uma entrega real e preservando o payload para auditoria.
/// </summary>
public sealed class FileSystemMailProvider : IMailProvider
{
    private readonly FileSystemMailProviderOptions _options;

    public FileSystemMailProvider(FileSystemMailProviderOptions options)
    {
        _options = options ?? throw new ArgumentNullException(nameof(options));

        if (string.IsNullOrWhiteSpace(_options.OutboxDirectory))
        {
            throw new ArgumentException("O diretório de saída é obrigatório.", nameof(options));
        }
    }

    public async Task<MailSendResult> SendAsync(MailSendRequest request, CancellationToken cancellationToken = default)
    {
        if (request is null)
        {
            throw new ArgumentNullException(nameof(request));
        }

        Directory.CreateDirectory(_options.OutboxDirectory);

        var messageId = Guid.NewGuid().ToString("N");
        var threadId = _options.DefaultThreadId;
        var timestamp = DateTimeOffset.UtcNow;
        var fileName = $"{timestamp:yyyyMMddHHmmssfff}_{request.TrackingId}_{messageId}.eml";
        var path = Path.Combine(_options.OutboxDirectory, fileName);

        var builder = new StringBuilder();
        builder.AppendLine($"Message-Id: {messageId}");
        builder.AppendLine($"Thread-Id: {threadId ?? string.Empty}");
        builder.AppendLine($"Account: {request.Account.Id} - {request.Account.DisplayName}");
        builder.AppendLine($"Tracking-Id: {request.TrackingId}");
        builder.AppendLine($"Subject: {request.Content.Subject}");
        builder.AppendLine($"To: {string.Join(", ", request.Envelope.To.Select(x => x.ToString()))}");
        if (request.Envelope.Cc.Any())
        {
            builder.AppendLine($"Cc: {string.Join(", ", request.Envelope.Cc.Select(x => x.ToString()))}");
        }
        if (request.Envelope.Bcc.Any())
        {
            builder.AppendLine($"Bcc: {string.Join(", ", request.Envelope.Bcc.Select(x => x.ToString()))}");
        }

        builder.AppendLine();
        builder.AppendLine(request.Content.HtmlBody);

        await File.WriteAllTextAsync(path, builder.ToString(), Encoding.UTF8, cancellationToken).ConfigureAwait(false);

        return new MailSendResult(messageId, threadId, timestamp);
    }
}
