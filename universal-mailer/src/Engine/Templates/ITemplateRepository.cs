namespace UniversalMailer.Engine.Templates;

public interface ITemplateRepository
{
    Task<TemplateDefinition> GetAsync(string key, CancellationToken cancellationToken = default);
}
