namespace UniversalMailer.Core.Security;

/// <summary>
/// Abstrai o armazenamento seguro de segredos em sistemas operacionais suportados.
/// </summary>
public interface ISecretStore
{
    /// <summary>
    /// Persiste um segredo e retorna um identificador opaco.
    /// </summary>
    /// <param name="name">Nome lógico do segredo.</param>
    /// <param name="secret">Valor em texto plano.</param>
    /// <returns>Referência segura para resgate futuro.</returns>
    string StoreSecret(string name, string secret);

    /// <summary>
    /// Recupera o valor associado a uma referência segura.
    /// </summary>
    /// <param name="reference">Identificador retornado na gravação.</param>
    /// <returns>Valor em texto plano.</returns>
    string RetrieveSecret(string reference);

    /// <summary>
    /// Indica se o valor informado já representa uma referência segura.
    /// </summary>
    bool IsReference(string value);
}
