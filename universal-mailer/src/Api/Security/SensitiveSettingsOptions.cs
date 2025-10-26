namespace UniversalMailer.Api.Security;

/// <summary>
/// Configura chaves sensíveis que devem ser protegidas em provedores de e-mail.
/// </summary>
public sealed class SensitiveSettingsOptions
{
    public ISet<string> Keys { get; } = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {
        "clientSecret",
        "oauthClientSecret",
        "refreshToken"
    };

    public string Mask { get; set; } = "••••••";

    public string CredentialPrefix { get; set; } = "universal-mailer";
}
