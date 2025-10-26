using System.Collections.Immutable;

namespace UniversalMailer.Core.Mail.Models;

/// <summary>
/// Representa os destinatários de um envio de e-mail, com coleções imutáveis para garantir rastreabilidade.
/// </summary>
public sealed class MailEnvelope
{
    public MailEnvelope(
        IEnumerable<MailAddress> to,
        IEnumerable<MailAddress>? cc = null,
        IEnumerable<MailAddress>? bcc = null)
    {
        To = to?.Where(address => address is not null).ToImmutableArray() ?? ImmutableArray<MailAddress>.Empty;
        Cc = cc?.Where(address => address is not null).ToImmutableArray() ?? ImmutableArray<MailAddress>.Empty;
        Bcc = bcc?.Where(address => address is not null).ToImmutableArray() ?? ImmutableArray<MailAddress>.Empty;

        if (To.IsDefaultOrEmpty)
        {
            throw new ArgumentException("É obrigatório informar ao menos um destinatário em 'Para'.", nameof(to));
        }
    }

    public ImmutableArray<MailAddress> To { get; }

    public ImmutableArray<MailAddress> Cc { get; }

    public ImmutableArray<MailAddress> Bcc { get; }
}
