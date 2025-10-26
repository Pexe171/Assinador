using System.Text;

namespace UniversalMailer.Engine.Templates;

/// <summary>
/// Realiza a renderização simples de templates com placeholders no formato {{CHAVE}}.
/// </summary>
public sealed class TemplateRenderer
{
    private readonly string _templatesDirectory;

    public TemplateRenderer(string templatesDirectory)
    {
        if (string.IsNullOrWhiteSpace(templatesDirectory))
        {
            throw new ArgumentException("O diretório de templates é obrigatório.", nameof(templatesDirectory));
        }

        _templatesDirectory = templatesDirectory;
    }

    public async Task<string> RenderBodyAsync(TemplateDefinition definition, IReadOnlyDictionary<string, string> values, CancellationToken cancellationToken = default)
    {
        var path = definition.ResolveBodyFullPath(_templatesDirectory);
        if (!File.Exists(path))
        {
            throw new FileNotFoundException($"Template não encontrado: {path}");
        }

        var content = await File.ReadAllTextAsync(path, Encoding.UTF8, cancellationToken).ConfigureAwait(false);
        return Replace(content, values);
    }

    public string RenderSubject(TemplateDefinition definition, IReadOnlyDictionary<string, string> values)
        => Replace(definition.SubjectTemplate, values);

    private static string Replace(string template, IReadOnlyDictionary<string, string> values)
    {
        if (values.Count == 0)
        {
            return template;
        }

        var builder = new StringBuilder(template);
        foreach (var (key, value) in values)
        {
            builder.Replace($"{{{{{key}}}}}", value ?? string.Empty);
        }

        return builder.ToString();
    }
}
