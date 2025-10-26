namespace UniversalMailer.Watcher.Imap;

/// <summary>
/// Configurações do monitoramento IMAP (polling ou IDLE).
/// </summary>
public sealed record ImapWatcherOptions
{
    public IReadOnlyCollection<string> AccountIds { get; init; } = Array.Empty<string>();

    public TimeSpan PollInterval { get; init; } = TimeSpan.FromMinutes(2);

    public TimeSpan DefaultLookback { get; init; } = TimeSpan.FromHours(6);

    public DateTimeOffset? InitialSince { get; init; }
}
