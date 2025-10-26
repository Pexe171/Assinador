using UniversalMailer.Api.Contracts.Emails;
using UniversalMailer.Api.Contracts.Returns;

namespace UniversalMailer.Api.Contracts.Search;

public sealed record SearchResponse(
    IReadOnlyCollection<EmailSummaryResponse> Envios,
    IReadOnlyCollection<ReturnSummaryResponse> Retornos);

public sealed record EmailSummaryResponse(
    string Protocolo,
    string Template,
    string Conta,
    DateTimeOffset EnviadoEm,
    IReadOnlyCollection<string> Destinatarios,
    string MensagemId);

public sealed record ReturnSummaryResponse(
    string Protocolo,
    string Status,
    DateTimeOffset RecebidoEm,
    string Assunto,
    string Conta);
