namespace UniversalMailer.Core.Mail.Models;

/// <summary>
/// Representa uma conta remetente configurada para envio.
/// </summary>
public sealed record MailAccount(string Id, string DisplayName)
{
    public string Id { get; } = Id;

    public string DisplayName { get; } = DisplayName;

    public override string ToString() => DisplayName;
}
