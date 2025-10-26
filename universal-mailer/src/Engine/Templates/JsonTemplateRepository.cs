using System.Text.Json;

namespace UniversalMailer.Engine.Templates;

/// <summary>
/// Carrega templates a partir de um manifesto JSON compartilhado com a aplicação WPF.
/// </summary>
public sealed class JsonTemplateRepository : ITemplateRepository
{
    private readonly string _manifestPath;
    private readonly SemaphoreSlim _mutex = new(1, 1);
    private IReadOnlyDictionary<string, TemplateDefinition>? _cache;

    public JsonTemplateRepository(string manifestPath)
    {
        if (string.IsNullOrWhiteSpace(manifestPath))
        {
            throw new ArgumentException("O caminho do manifesto é obrigatório.", nameof(manifestPath));
        }

        _manifestPath = manifestPath;
    }

    public async Task<TemplateDefinition> GetAsync(string key, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(key))
        {
            throw new ArgumentException("A chave do template é obrigatória.", nameof(key));
        }

        var dictionary = await LoadAsync(cancellationToken).ConfigureAwait(false);
        if (!dictionary.TryGetValue(key, out var definition))
        {
            throw new InvalidOperationException($"Template '{key}' não encontrado no manifesto.");
        }

        return definition;
    }

    private async Task<IReadOnlyDictionary<string, TemplateDefinition>> LoadAsync(CancellationToken cancellationToken)
    {
        if (_cache is not null)
        {
            return _cache;
        }

        await _mutex.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            if (_cache is not null)
            {
                return _cache;
            }

            await using var stream = File.OpenRead(_manifestPath);
            var payload = await JsonSerializer.DeserializeAsync<TemplateManifest>(
                stream,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true },
                cancellationToken).ConfigureAwait(false);

            if (payload?.Templates is null || payload.Templates.Count == 0)
            {
                throw new InvalidOperationException("Nenhum template foi definido no manifesto.");
            }

            _cache = payload.Templates.ToDictionary(
                pair => pair.Key,
                pair => new TemplateDefinition
                {
                    Key = pair.Key,
                    DisplayName = pair.Value.DisplayName ?? pair.Key,
                    Version = pair.Value.Version ?? "1.0.0",
                    SubjectTemplate = pair.Value.SubjectTemplate ?? throw new InvalidOperationException($"Template '{pair.Key}' sem assunto."),
                    BodyPath = pair.Value.BodyPath ?? throw new InvalidOperationException($"Template '{pair.Key}' sem caminho de corpo."),
                },
                StringComparer.OrdinalIgnoreCase);

            return _cache;
        }
        finally
        {
            _mutex.Release();
        }
    }

    private sealed class TemplateManifest
    {
        public Dictionary<string, TemplatePayload> Templates { get; set; } = new(StringComparer.OrdinalIgnoreCase);
    }

    private sealed class TemplatePayload
    {
        public string? DisplayName { get; set; }

        public string? Version { get; set; }

        public string? SubjectTemplate { get; set; }

        public string? BodyPath { get; set; }
    }
}
