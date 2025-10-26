using System.Text.RegularExpressions;

namespace UniversalMailer.Core.Returns.Processing;

/// <summary>
/// Utilitário para localizar o identificador AC-#### em assuntos ou corpos de e-mail.
/// </summary>
public static partial class ReturnTrackingIdExtractor
{
    [GeneratedRegex("AC-\\d{4,}", RegexOptions.IgnoreCase | RegexOptions.CultureInvariant | RegexOptions.Compiled)]
    private static partial Regex TrackingRegex();

    public static string? Extract(string? subject, string? body)
    {
        var source = string.Join(" ", new[] { subject, body }
            .Where(static part => !string.IsNullOrWhiteSpace(part))
            .Select(static part => part!.Trim()));

        if (string.IsNullOrWhiteSpace(source))
        {
            return null;
        }

        var match = TrackingRegex().Match(source);
        return match.Success ? match.Value.ToUpperInvariant() : null;
    }
}
