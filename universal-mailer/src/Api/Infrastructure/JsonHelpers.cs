using System.Text.Json;

namespace UniversalMailer.Api.Infrastructure;

internal static class JsonHelpers
{
    private static readonly JsonSerializerOptions Options = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false
    };

    public static string SerializeDictionary(IReadOnlyDictionary<string, string>? values)
        => JsonSerializer.Serialize(values ?? new Dictionary<string, string>(), Options);

    public static IReadOnlyDictionary<string, string> DeserializeDictionary(string? json)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return new Dictionary<string, string>();
        }

        return JsonSerializer.Deserialize<Dictionary<string, string>>(json, Options)
               ?? new Dictionary<string, string>();
    }
}
