using System.Linq;
using System.Text;
using System.Text.Json;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Core.Mail.Records;

namespace UniversalMailer.Persistence.Stores;

/// <summary>
/// Persiste os envios em um arquivo JSONL para facilitar auditorias simples.
/// </summary>
public sealed class FileMailDispatchStore : IMailDispatchStore
{
    private readonly string _filePath;
    private readonly JsonSerializerOptions _serializerOptions = new()
    {
        WriteIndented = false,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
    };

    public FileMailDispatchStore(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath))
        {
            throw new ArgumentException("O caminho do arquivo é obrigatório.", nameof(filePath));
        }

        _filePath = filePath;
    }

    public async Task SaveAsync(MailDispatchRecord record, CancellationToken cancellationToken = default)
    {
        if (record is null)
        {
            throw new ArgumentNullException(nameof(record));
        }

        cancellationToken.ThrowIfCancellationRequested();

        var directory = Path.GetDirectoryName(_filePath);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var payload = new PersistedMailDispatch(record);
        var json = JsonSerializer.Serialize(payload, _serializerOptions);

        await using var stream = new FileStream(_filePath, FileMode.Append, FileAccess.Write, FileShare.Read);
        await using var writer = new StreamWriter(stream, Encoding.UTF8);
        await writer.WriteLineAsync(json);
        await writer.FlushAsync();
    }

    private sealed record PersistedMailDispatch
    {
        public PersistedMailDispatch(MailDispatchRecord source)
        {
            TrackingId = source.TrackingId;
            TemplateKey = source.TemplateKey;
            TemplateVersion = source.TemplateVersion;
            AccountId = source.Account.Id;
            AccountName = source.Account.DisplayName;
            MessageId = source.Result.MessageId;
            ThreadId = source.Result.ThreadId;
            SentAt = source.Result.SentAt;
            LoggedAt = source.CreatedAt;
            To = source.Envelope.To.Select(Map).ToArray();
            Cc = source.Envelope.Cc.Select(Map).ToArray();
            Bcc = source.Envelope.Bcc.Select(Map).ToArray();
        }

        public string TrackingId { get; }

        public string TemplateKey { get; }

        public string TemplateVersion { get; }

        public string AccountId { get; }

        public string AccountName { get; }

        public string MessageId { get; }

        public string? ThreadId { get; }

        public DateTimeOffset SentAt { get; }

        public DateTimeOffset LoggedAt { get; }

        public Participant[] To { get; }

        public Participant[] Cc { get; }

        public Participant[] Bcc { get; }

        private static Participant Map(MailAddress address)
            => new(address.Email, address.Name);
    }

    private sealed record Participant(string Email, string? Name);
}
