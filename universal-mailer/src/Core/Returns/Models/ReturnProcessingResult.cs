namespace UniversalMailer.Core.Returns.Models;

/// <summary>
/// Resultado consolidado após processar um retorno.
/// </summary>
public sealed record ReturnProcessingResult(
    ReturnRecord Record,
    ReturnThread Thread,
    bool IsNewThread,
    bool IsDuplicate);
