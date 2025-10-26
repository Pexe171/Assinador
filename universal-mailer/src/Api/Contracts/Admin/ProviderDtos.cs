using UniversalMailer.Core.Mail.Contracts;

namespace UniversalMailer.Api.Contracts.Admin;

public sealed class UpsertProviderRequest
{
    public string Name { get; set; } = string.Empty;

    public string DisplayName { get; set; } = string.Empty;

    public MailProviderType Tipo { get; set; } = MailProviderType.FileSystem;

    public Dictionary<string, string> Configuracoes { get; set; } = new(StringComparer.OrdinalIgnoreCase);

    public bool Ativo { get; set; } = true;

    public List<UpsertAccountRequest> Contas { get; set; } = new();
}

public sealed class UpsertAccountRequest
{
    public string AccountId { get; set; } = string.Empty;

    public string Address { get; set; } = string.Empty;

    public string? DisplayName { get; set; }

    public Dictionary<string, string> Metadata { get; set; } = new(StringComparer.OrdinalIgnoreCase);

    public bool Ativo { get; set; } = true;
}

public sealed record ProviderResponse(
    Guid Id,
    string NomeInterno,
    string NomeExibicao,
    string Tipo,
    IReadOnlyDictionary<string, string> Configuracoes,
    bool Ativo,
    DateTimeOffset CriadoEm,
    DateTimeOffset AtualizadoEm,
    IReadOnlyCollection<AccountResponse> Contas);

public sealed record AccountResponse(
    Guid Id,
    string AccountId,
    string Address,
    string NomeExibicao,
    IReadOnlyDictionary<string, string> Metadata,
    bool Ativo,
    DateTimeOffset CriadoEm,
    DateTimeOffset AtualizadoEm);
