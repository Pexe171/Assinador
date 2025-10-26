namespace UniversalMailer.Api.Contracts.Emails;

public sealed record SendEmailResponse(
    string Protocolo,
    string MensagemId,
    string? ThreadId,
    DateTimeOffset EnviadoEm);
