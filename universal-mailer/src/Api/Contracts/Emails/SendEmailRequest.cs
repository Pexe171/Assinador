namespace UniversalMailer.Api.Contracts.Emails;

public sealed class SendEmailRequest
{
    public string AccountId { get; set; } = string.Empty;

    public string TemplateKey { get; set; } = string.Empty;

    public Dictionary<string, string> Variaveis { get; set; } = new(StringComparer.OrdinalIgnoreCase);

    public List<EmailRecipientInput> Para { get; set; } = new();

    public List<EmailRecipientInput> Cc { get; set; } = new();

    public List<EmailRecipientInput> Bcc { get; set; } = new();
}

public sealed record EmailRecipientInput(string Email, string? Nome);
