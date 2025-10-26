using System.Collections.Immutable;
using System.Linq;
using UniversalMailer.Core.Mail.Models;

namespace UniversalMailer.Core.Mail.Policies;

/// <summary>
/// Implementação padrão para limpar destinatários e aplicar regras de segurança.
/// </summary>
public sealed class MailRecipientPolicy : IMailRecipientPolicy
{
    private readonly MailRecipientPolicyOptions _options;
    private readonly ISet<string> _ccDomains;

    public MailRecipientPolicy(MailRecipientPolicyOptions options)
    {
        _options = options ?? throw new ArgumentNullException(nameof(options));
        _ccDomains = options.CcDomainWhitelist ?? new HashSet<string>(StringComparer.OrdinalIgnoreCase);
    }

    public MailRecipientSet Apply(
        IEnumerable<MailAddress> to,
        IEnumerable<MailAddress>? cc,
        IEnumerable<MailAddress>? bcc)
    {
        if (to is null)
        {
            throw new ArgumentNullException(nameof(to));
        }

        var comparer = StringComparer.OrdinalIgnoreCase;

        var toList = Sanitize(to, comparer);
        if (toList.Count == 0)
        {
            throw new InvalidOperationException("É obrigatório informar pelo menos um destinatário em 'Para'.");
        }

        var seen = new HashSet<string>(toList.Select(NormalizeEmail), comparer);

        var ccList = SanitizeCc(cc, seen);
        foreach (var address in ccList)
        {
            seen.Add(NormalizeEmail(address));
        }

        var bccList = SanitizeBcc(bcc, seen);

        return new MailRecipientSet(toList, ccList, bccList);
    }

    private IReadOnlyCollection<MailAddress> Sanitize(
        IEnumerable<MailAddress> source,
        StringComparer comparer)
    {
        var unique = new HashSet<string>(comparer);
        var result = new List<MailAddress>();

        foreach (var address in source.Where(static address => address is not null))
        {
            var normalized = NormalizeEmail(address);
            if (unique.Add(normalized))
            {
                result.Add(address);
            }
        }

        return result.ToImmutableArray();
    }

    private IReadOnlyCollection<MailAddress> SanitizeCc(
        IEnumerable<MailAddress>? source,
        ISet<string> seen)
    {
        if (source is null)
        {
            return ImmutableArray<MailAddress>.Empty;
        }

        var result = new List<MailAddress>();

        foreach (var address in source.Where(static address => address is not null))
        {
            var normalized = NormalizeEmail(address);
            if (seen.Contains(normalized))
            {
                continue;
            }

            ValidateCcDomain(address);

            seen.Add(normalized);
            result.Add(address);
        }

        return result.ToImmutableArray();
    }

    private IReadOnlyCollection<MailAddress> SanitizeBcc(
        IEnumerable<MailAddress>? source,
        ISet<string> seen)
    {
        if (source is null)
        {
            return ImmutableArray<MailAddress>.Empty;
        }

        var result = new List<MailAddress>();

        foreach (var address in source.Where(static address => address is not null))
        {
            var normalized = NormalizeEmail(address);
            if (seen.Contains(normalized))
            {
                continue;
            }

            seen.Add(normalized);
            result.Add(address);
        }

        return result.ToImmutableArray();
    }

    private void ValidateCcDomain(MailAddress address)
    {
        if (_ccDomains.Count == 0)
        {
            return;
        }

        var email = address.Email ?? string.Empty;
        var domain = ExtractDomain(email);

        if (!_ccDomains.Contains(domain))
        {
            var message = string.IsNullOrWhiteSpace(_options.DomainBlockedMessage)
                ? $"Domínio '{domain}' não permitido para cópias."
                : $"{_options.DomainBlockedMessage} ({domain}).";

            throw new InvalidOperationException(message);
        }
    }

    private static string NormalizeEmail(MailAddress address)
    {
        var email = address.Email ?? throw new InvalidOperationException("Endereço de e-mail inválido.");
        return email.Trim();
    }

    private static string ExtractDomain(string email)
    {
        var atIndex = email.LastIndexOf('@');
        if (atIndex < 0 || atIndex == email.Length - 1)
        {
            throw new InvalidOperationException($"Endereço de e-mail inválido: '{email}'.");
        }

        return email[(atIndex + 1)..].Trim();
    }
}
