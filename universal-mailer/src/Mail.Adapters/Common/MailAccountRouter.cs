using System;
using System.Collections.Generic;
using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Mail.Adapters.Common;

/// <summary>
/// Responsável por conectar cada conta configurada ao adapter correto.
/// </summary>
public sealed class MailAccountRouter
{
    private readonly MailProviderRegistry _registry;
    private readonly IDictionary<string, MailAccount> _accounts;

    public MailAccountRouter(MailProviderRegistry registry, IDictionary<string, MailAccount> accounts)
    {
        _registry = registry ?? throw new ArgumentNullException(nameof(registry));
        _accounts = accounts ?? throw new ArgumentNullException(nameof(accounts));
    }

    public MailAccount GetAccount(string accountId)
    {
        if (!_accounts.TryGetValue(accountId, out var account))
        {
            throw new KeyNotFoundException($"Conta de e-mail '{accountId}' não foi registrada.");
        }

        return account;
    }

    public IMailProvider ResolveProvider(string accountId)
    {
        var account = GetAccount(accountId);
        return _registry.Resolve(account.Provider);
    }
}
