using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Core.Returns.Contracts;

/// <summary>
/// Responsável por orquestrar o envio de follow-ups automáticos.
/// </summary>
public interface IReturnFollowUpDispatcher
{
    Task<ReturnFollowUpResult> SendFollowUpAsync(ReturnThread thread, CancellationToken cancellationToken = default);
}
