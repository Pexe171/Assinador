namespace UniversalMailer.Core.Returns.Processing;

/// <summary>
/// Representa uma regra simples de palavra-chave utilizada na classificação automática.
/// </summary>
public sealed record KeywordRule(string Term, double Weight = 1.0, KeywordRuleScope Scope = KeywordRuleScope.SubjectOrBody)
{
    public string Term { get; } = Term.Trim();

    public double Weight { get; } = Weight;

    public KeywordRuleScope Scope { get; } = Scope;
}

/// <summary>
/// Define onde a palavra-chave deve ser buscada.
/// </summary>
public enum KeywordRuleScope
{
    Subject,
    Body,
    SubjectOrBody
}
