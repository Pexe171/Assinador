using Microsoft.EntityFrameworkCore;
using UniversalMailer.Api.Infrastructure;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Mail.Adapters.Common;
using UniversalMailer.Persistence.Db;

namespace UniversalMailer.Api.Services;

public sealed class DispatchContextFactory
{
    private readonly MailerDbContext _context;
    private readonly MailProviderRegistry _registry;

    public DispatchContextFactory(MailerDbContext context, MailProviderRegistry registry)
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
        _registry = registry ?? throw new ArgumentNullException(nameof(registry));
    }

    public async Task<DispatchContext> CreateAsync(string accountId, CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(accountId))
        {
            throw new ArgumentException("A conta remetente é obrigatória.", nameof(accountId));
        }

        var account = await _context.MailAccounts
            .AsNoTracking()
            .Include(entity => entity.Provider)
            .FirstOrDefaultAsync(entity => entity.AccountId == accountId && entity.IsActive, cancellationToken)
            .ConfigureAwait(false);

        if (account is null)
        {
            throw new InvalidOperationException($"Conta '{accountId}' não encontrada ou inativa.");
        }

        if (!account.Provider.IsActive)
        {
            throw new InvalidOperationException($"O provedor '{account.Provider.DisplayName}' está inativo.");
        }

        var settings = JsonHelpers.DeserializeDictionary(account.Provider.SettingsJson);
        var descriptor = new MailProviderDescriptor(account.Provider.Name, account.Provider.Type, settings);
        var provider = _registry.Resolve(descriptor);

        var displayName = string.IsNullOrWhiteSpace(account.DisplayName)
            ? account.Address
            : account.DisplayName;

        var domainAccount = new MailAccount(account.AccountId, displayName);

        return new DispatchContext(domainAccount, provider);
    }
}

public sealed record DispatchContext(MailAccount Account, IMailProvider Provider);
