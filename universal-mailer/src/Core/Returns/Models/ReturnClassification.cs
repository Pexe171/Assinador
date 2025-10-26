using System.Collections.ObjectModel;

namespace UniversalMailer.Core.Returns.Models;

/// <summary>
/// Resultado detalhado da etapa de classificação automática.
/// </summary>
public sealed record ReturnClassification
{
    public ReturnClassification(
        ReturnStatus status,
        double score,
        IReadOnlyCollection<string> matchedKeywords,
        IReadOnlyCollection<string> reasons,
        bool requiresManualReview)
    {
        Status = status;
        Score = score;
        MatchedKeywords = matchedKeywords ?? Array.Empty<string>();
        Reasons = reasons ?? Array.Empty<string>();
        RequiresManualReview = requiresManualReview;
    }

    public ReturnStatus Status { get; init; }

    public double Score { get; init; }

    public IReadOnlyCollection<string> MatchedKeywords { get; init; }

    public IReadOnlyCollection<string> Reasons { get; init; }

    public bool RequiresManualReview { get; init; }

    public ReturnClassification WithStatus(
        ReturnStatus status,
        IEnumerable<string>? extraReasons = null,
        bool? requiresManualReview = null)
    {
        var reasons = new List<string>(Reasons);

        if (extraReasons is not null)
        {
            foreach (var reason in extraReasons)
            {
                if (!string.IsNullOrWhiteSpace(reason))
                {
                    reasons.Add(reason.Trim());
                }
            }
        }

        return this with
        {
            Status = status,
            Reasons = new ReadOnlyCollection<string>(reasons),
            RequiresManualReview = requiresManualReview ?? RequiresManualReview
        };
    }

    public static ReturnClassification Manual(params string[] reasons)
    {
        var details = reasons?.Where(static reason => !string.IsNullOrWhiteSpace(reason))
            .Select(static reason => reason.Trim())
            .ToArray() ?? Array.Empty<string>();

        return new ReturnClassification(ReturnStatus.Manual, 0, Array.Empty<string>(), details, true);
    }

    public static ReturnClassification Duplicate(string trackingKey, int occurrenceNumber)
    {
        var reason = $"Retorno duplicado: {occurrenceNumber}ª mensagem para o protocolo {trackingKey}.";
        return new ReturnClassification(ReturnStatus.Duplo, occurrenceNumber, Array.Empty<string>(), new[] { reason }, true);
    }
}
