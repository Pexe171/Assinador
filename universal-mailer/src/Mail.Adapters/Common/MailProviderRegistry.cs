using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;
using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Mail.Adapters.Common;

/// <summary>
/// Controla o registro e a seleção dinâmica de adapters a partir do tipo configurado para cada conta.
/// </summary>
public sealed class MailProviderRegistry
{
    private readonly ImmutableDictionary<MailProviderType, Func<MailProviderDescriptor, IMailProvider>> _factories;

    public MailProviderRegistry(IDictionary<MailProviderType, Func<MailProviderDescriptor, IMailProvider>> factories)
    {
        if (factories is null || factories.Count == 0)
        {
            throw new ArgumentException("É necessário informar ao menos uma fábrica de adapters.", nameof(factories));
        }

        _factories = factories.ToImmutableDictionary();
    }

    /// <summary>
    /// Cria uma instância de provider com base no descriptor de configuração.
    /// </summary>
    public IMailProvider Resolve(MailProviderDescriptor descriptor)
    {
        if (!_factories.TryGetValue(descriptor.Type, out var factory))
        {
            var supported = string.Join(", ", _factories.Keys.Select(x => x.ToString()));
            throw new NotSupportedException($"Nenhum adapter cadastrado para o tipo '{descriptor.Type}'. Tipos disponíveis: {supported}.");
        }

        return factory(descriptor);
    }
}
