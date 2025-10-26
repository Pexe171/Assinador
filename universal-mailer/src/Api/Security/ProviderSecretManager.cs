using UniversalMailer.Core.Security;

namespace UniversalMailer.Api.Security;

/// <summary>
/// Aplica regras de proteção e mascaramento para configurações sensíveis de provedores.
/// </summary>
public sealed class ProviderSecretManager
{
    private readonly ISecretStore _secretStore;
    private readonly SensitiveSettingsOptions _options;

    public ProviderSecretManager(ISecretStore secretStore, SensitiveSettingsOptions options)
    {
        _secretStore = secretStore ?? throw new ArgumentNullException(nameof(secretStore));
        _options = options ?? throw new ArgumentNullException(nameof(options));
    }

    public IReadOnlyDictionary<string, string> Protect(
        string providerName,
        IReadOnlyDictionary<string, string> settings,
        IReadOnlyDictionary<string, string>? existing = null)
    {
        if (settings is null)
        {
            throw new ArgumentNullException(nameof(settings));
        }

        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        existing ??= new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var processedKeys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        foreach (var pair in settings)
        {
            processedKeys.Add(pair.Key);

            if (!IsSensitive(pair.Key))
            {
                result[pair.Key] = pair.Value;
                continue;
            }

            if (string.IsNullOrWhiteSpace(pair.Value) || string.Equals(pair.Value, _options.Mask, StringComparison.Ordinal))
            {
                if (existing.TryGetValue(pair.Key, out var current) && !string.IsNullOrWhiteSpace(current))
                {
                    result[pair.Key] = current;
                }

                continue;
            }

            if (_secretStore.IsReference(pair.Value))
            {
                result[pair.Key] = pair.Value;
                continue;
            }

            var reference = _secretStore.StoreSecret(BuildSecretName(providerName, pair.Key), pair.Value);
            result[pair.Key] = reference;
        }

        foreach (var pair in existing)
        {
            if (result.ContainsKey(pair.Key) || processedKeys.Contains(pair.Key))
            {
                continue;
            }

            if (IsSensitive(pair.Key) && !string.IsNullOrWhiteSpace(pair.Value))
            {
                result[pair.Key] = pair.Value;
            }
        }

        return result;
    }

    public IReadOnlyDictionary<string, string> MaskForResponse(IReadOnlyDictionary<string, string> stored)
    {
        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        foreach (var pair in stored)
        {
            result[pair.Key] = IsSensitive(pair.Key) && !string.IsNullOrWhiteSpace(pair.Value)
                ? _options.Mask
                : pair.Value;
        }

        return result;
    }

    public IReadOnlyDictionary<string, string> ResolveForRuntime(IReadOnlyDictionary<string, string> stored)
    {
        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        foreach (var pair in stored)
        {
            if (!IsSensitive(pair.Key))
            {
                result[pair.Key] = pair.Value;
                continue;
            }

            if (string.IsNullOrWhiteSpace(pair.Value))
            {
                continue;
            }

            var value = _secretStore.IsReference(pair.Value)
                ? _secretStore.RetrieveSecret(pair.Value)
                : pair.Value;

            result[pair.Key] = value;
        }

        return result;
    }

    private bool IsSensitive(string key) => _options.Keys.Contains(key);

    private string BuildSecretName(string providerName, string key)
    {
        var normalizedProvider = string.IsNullOrWhiteSpace(providerName) ? "provider" : providerName.Trim();
        return $"{_options.CredentialPrefix}/{normalizedProvider}/{key}";
    }
}
