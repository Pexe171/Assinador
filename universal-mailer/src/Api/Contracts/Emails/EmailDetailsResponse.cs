namespace UniversalMailer.Api.Contracts.Emails;

public sealed record EmailDetailsResponse(
    string Protocolo,
    string Template,
    string VersaoTemplate,
    EmailAccountSummary Conta,
    string MensagemId,
    string? ThreadId,
    DateTimeOffset EnviadoEm,
    DateTimeOffset RegistradoEm,
    IReadOnlyCollection<EmailRecipientSummary> Destinatarios);

public sealed record EmailAccountSummary(string Id, string Nome);

public sealed record EmailRecipientSummary(string Tipo, string Email, string? Nome);
