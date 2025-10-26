namespace UniversalMailer.Core.Mail.Policies;

/// <summary>
/// Configurações para o filtro de destinatários.
/// </summary>
public sealed class MailRecipientPolicyOptions
{
    /// <summary>
    /// Domínios autorizados para cópias (CC). Quando vazio, todos os domínios são aceitos.
    /// </summary>
    public ISet<string> CcDomainWhitelist { get; } = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

    /// <summary>
    /// Mensagem padrão para indicar que um endereço foi bloqueado.
    /// </summary>
    public string DomainBlockedMessage { get; set; } = "Domínio não autorizado para destinatários em cópia.";
}
