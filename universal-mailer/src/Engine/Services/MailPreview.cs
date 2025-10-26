namespace UniversalMailer.Engine.Services;

/// <summary>
/// Resultado da prévia obrigatória.
/// </summary>
public sealed class MailPreview
{
    public MailPreview(string trackingId, string subject, string bodyHtml, string templateVersion)
    {
        TrackingId = trackingId;
        Subject = subject;
        BodyHtml = bodyHtml;
        TemplateVersion = templateVersion;
    }

    public string TrackingId { get; }

    public string Subject { get; }

    public string BodyHtml { get; }

    public string TemplateVersion { get; }
}
