namespace UniversalMailer.Core.Returns.Models;

/// <summary>
/// Classificação final de um retorno recebido via e-mail.
/// </summary>
public enum ReturnStatus
{
    Validado,
    Invalidado,
    Complementar,
    Duplo,
    Manual
}
