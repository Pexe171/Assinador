using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Core.Returns.Contracts;

/// <summary>
/// Responsável por atribuir uma classificação inicial ao retorno com base no conteúdo recebido.
/// </summary>
public interface IReturnClassifier
{
    Task<ReturnClassification> ClassifyAsync(ReturnMessage message, CancellationToken cancellationToken = default);
}
