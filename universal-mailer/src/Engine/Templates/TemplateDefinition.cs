using System;
using System.IO;

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

    /// <summary>
    /// Caminho relativo para templates armazenados em disco.
    /// </summary>
    public string? BodyPath { get; init; }

    /// <summary>
    /// Conteúdo HTML inline armazenado no banco.
    /// </summary>
    public string? BodyHtml { get; init; }

    public string ResolveBodyFullPath(string baseDirectory)
    {
        if (string.IsNullOrWhiteSpace(BodyPath))
        {
            throw new InvalidOperationException("O template atual não possui arquivo físico associado.");
        }

        return Path.Combine(baseDirectory, BodyPath);
    }

    public bool HasInlineBody => !string.IsNullOrWhiteSpace(BodyHtml);
}
