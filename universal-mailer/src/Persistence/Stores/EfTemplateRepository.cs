using Microsoft.EntityFrameworkCore;
using UniversalMailer.Engine.Templates;
using UniversalMailer.Persistence.Db;

namespace UniversalMailer.Persistence.Stores;

/// <summary>
/// Repositório de templates baseado em banco relacional.
/// </summary>
public sealed class EfTemplateRepository : ITemplateRepository
{
    private readonly MailerDbContext _context;

    public EfTemplateRepository(MailerDbContext context)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }

    public async Task<TemplateDefinition> GetAsync(string key, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(key))
        {
            throw new ArgumentException("A chave do template é obrigatória.", nameof(key));
        }

        var entity = await _context.Templates
            .AsNoTracking()
            .FirstOrDefaultAsync(template => template.Key == key && template.IsActive, cancellationToken)
            .ConfigureAwait(false);

        if (entity is null)
        {
            throw new InvalidOperationException($"Template '{key}' não encontrado ou inativo.");
        }

        return new TemplateDefinition
        {
            Key = entity.Key,
            DisplayName = entity.DisplayName,
            Version = entity.Version,
            SubjectTemplate = entity.Subject,
            BodyHtml = entity.Body
        };
    }
}
