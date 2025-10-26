namespace UniversalMailer.Engine.Templates;

/// <summary>
/// Metadados do template utilizado para composição do e-mail.
/// </summary>
public sealed class TemplateDefinition
{
    public required string Key { get; init; }

    public required string DisplayName { get; init; }

    public required string Version { get; init; }

    public required string SubjectTemplate { get; init; }

    public required string BodyPath { get; init; }

    public string ResolveBodyFullPath(string baseDirectory)
        => Path.Combine(baseDirectory, BodyPath);
}
