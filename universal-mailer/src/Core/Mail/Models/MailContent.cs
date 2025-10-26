namespace UniversalMailer.Core.Mail.Models;

/// <summary>
/// Conteúdo do e-mail a ser enviado.
/// </summary>
public sealed record MailContent(string Subject, string HtmlBody)
{
    public string Subject { get; } = Subject;

    public string HtmlBody { get; } = HtmlBody;
}
