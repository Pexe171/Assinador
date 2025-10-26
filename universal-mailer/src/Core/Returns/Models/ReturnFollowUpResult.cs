namespace UniversalMailer.Core.Returns.Models;

/// <summary>
/// Resultado do disparo de follow-up automático para uma pendência de retorno.
/// </summary>
public sealed record ReturnFollowUpResult(
    string MessageId,
    string? ThreadId,
    DateTimeOffset SentAt);
