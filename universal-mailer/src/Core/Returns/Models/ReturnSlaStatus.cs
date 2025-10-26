namespace UniversalMailer.Core.Returns.Models;

/// <summary>
/// Representa o estágio de SLA de um retorno que ainda precisa de ação operacional.
/// </summary>
public enum ReturnSlaStatus
{
    EmDia,
    Atencao,
    Vencido
}
