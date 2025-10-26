namespace UniversalMailer.Core.Mail.Models;

/// <summary>
/// Representa um participante em um e-mail, mantendo nome opcional e endereço obrigatório.
/// </summary>
public sealed record MailAddress(string Email, string? Name = null)
{
    public string Email { get; } = Email.Trim();

    public string? Name { get; } = string.IsNullOrWhiteSpace(Name) ? null : Name.Trim();

    public override string ToString() => string.IsNullOrWhiteSpace(Name)
        ? Email
        : $"{Name} <{Email}>";
}
