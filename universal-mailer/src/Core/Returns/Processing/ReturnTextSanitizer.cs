using System.Net;
using System.Text.RegularExpressions;

namespace UniversalMailer.Core.Returns.Processing;

/// <summary>
/// Normaliza trechos de texto vindos de e-mails (HTML ou texto puro).
/// </summary>
public static partial class ReturnTextSanitizer
{
    [GeneratedRegex("<[^>]+>", RegexOptions.Compiled | RegexOptions.CultureInvariant)]
    private static partial Regex HtmlTagRegex();

    [GeneratedRegex("\\s+", RegexOptions.Compiled | RegexOptions.CultureInvariant)]
    private static partial Regex WhitespaceRegex();

    public static string Normalize(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return string.Empty;
        }

        var decoded = WebUtility.HtmlDecode(value);
        var withoutTags = HtmlTagRegex().Replace(decoded, " ");
        var normalized = WhitespaceRegex().Replace(withoutTags, " ").Trim();
        return normalized;
    }

    public static string BuildPreview(string source, int maxLength = 280)
    {
        if (string.IsNullOrWhiteSpace(source))
        {
            return string.Empty;
        }

        var trimmed = source.Trim();
        if (trimmed.Length <= maxLength)
        {
            return trimmed;
        }

        return trimmed[..maxLength] + "…";
    }
}
