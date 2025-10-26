namespace UniversalMailer.Api.Contracts.Returns;

public sealed record ReturnThreadResponse(
    string Protocolo,
    bool PossuiIdValido,
    string StatusSla,
    DateTimeOffset StatusSlaAtualizadoEm,
    DateTimeOffset CriadoEm,
    DateTimeOffset AtualizadoEm,
    DateTimeOffset? UltimoFollowUpEm,
    IReadOnlyCollection<ReturnMessageResponse> Mensagens);

public sealed record ReturnMessageResponse(
    string MensagemId,
    string Conta,
    string Provedor,
    string Remetente,
    string? NomeRemetente,
    string Assunto,
    string Corpo,
    string Status,
    double Score,
    IReadOnlyCollection<string> PalavrasChave,
    IReadOnlyCollection<string> Razoes,
    bool RevisaoManual,
    DateTimeOffset RecebidoEm,
    string? Conversa,
    IReadOnlyDictionary<string, string> Metadata);
