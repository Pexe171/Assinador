namespace UniversalMailer.Mail.Adapters.FileSystem;

/// <summary>
/// Configurações básicas para o provedor de arquivos, útil em ambientes de desenvolvimento.
/// </summary>
public sealed class FileSystemMailProviderOptions
{
    public required string OutboxDirectory { get; init; }

    public string? DefaultThreadId { get; init; }
}
