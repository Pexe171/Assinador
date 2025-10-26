using System.Globalization;
using UniversalMailer.Core.Returns.Contracts;
using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Core.Returns.Processing;

/// <summary>
/// Classificador baseado em palavras-chave ponderadas.
/// </summary>
public sealed class KeywordReturnClassifier : IReturnClassifier
{
    private readonly IReadOnlyDictionary<ReturnStatus, IReadOnlyCollection<KeywordRule>> _rules;

    public KeywordReturnClassifier(IReadOnlyDictionary<ReturnStatus, IReadOnlyCollection<KeywordRule>> rules)
    {
        _rules = rules ?? throw new ArgumentNullException(nameof(rules));
    }

    public Task<ReturnClassification> ClassifyAsync(ReturnMessage message, CancellationToken cancellationToken = default)
    {
        if (message is null)
        {
            throw new ArgumentNullException(nameof(message));
        }

        cancellationToken.ThrowIfCancellationRequested();

        var subject = message.Subject ?? string.Empty;
        var body = message.Body ?? string.Empty;

        var subjectComparison = CultureInfo.InvariantCulture.CompareInfo;
        var bodyComparison = subjectComparison;

        var scores = new Dictionary<ReturnStatus, double>();
        var matches = new Dictionary<ReturnStatus, List<string>>();

        foreach (var (status, rules) in _rules)
        {
            if (status is ReturnStatus.Duplo or ReturnStatus.Manual)
            {
                continue;
            }

            var statusScore = 0d;
            var statusMatches = new List<string>();

            foreach (var rule in rules)
            {
                if (string.IsNullOrWhiteSpace(rule.Term))
                {
                    continue;
                }

                var term = rule.Term;
                var contains = rule.Scope switch
                {
                    KeywordRuleScope.Subject => Contains(subjectComparison, subject, term),
                    KeywordRuleScope.Body => Contains(bodyComparison, body, term),
                    _ => Contains(subjectComparison, subject, term) || Contains(bodyComparison, body, term)
                };

                if (contains)
                {
                    statusScore += Math.Max(0.1, rule.Weight);
                    statusMatches.Add(term);
                }
            }

            if (statusScore > 0)
            {
                scores[status] = statusScore;
                matches[status] = statusMatches;
            }
        }

        if (scores.Count == 0)
        {
            return Task.FromResult(ReturnClassification.Manual("Nenhuma palavra-chave encontrada."));
        }

        var ordered = scores
            .OrderByDescending(static entry => entry.Value)
            .ThenBy(static entry => entry.Key)
            .ToList();

        var best = ordered[0];

        if (ordered.Count > 1 && Math.Abs(best.Value - ordered[1].Value) < double.Epsilon)
        {
            return Task.FromResult(ReturnClassification.Manual("Empate de pontuação entre classificações."));
        }

        var reasons = new List<string>
        {
            $"Pontuação {best.Value:0.##} para o status {best.Key}."
        };

        if (matches.TryGetValue(best.Key, out var matchedKeywords) && matchedKeywords.Count > 0)
        {
            reasons.Add($"Palavras-chave encontradas: {string.Join(", ", matchedKeywords)}.");
        }

        return Task.FromResult(new ReturnClassification(
            best.Key,
            best.Value,
            matches.TryGetValue(best.Key, out var bestMatches)
                ? bestMatches.AsReadOnly()
                : Array.Empty<string>(),
            reasons.AsReadOnly(),
            false));
    }

    private static bool Contains(CompareInfo compareInfo, string source, string term)
    {
        return compareInfo.IndexOf(source, term, CompareOptions.IgnoreCase | CompareOptions.IgnoreNonSpace) >= 0;
    }
}
