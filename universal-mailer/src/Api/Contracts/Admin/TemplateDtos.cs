namespace UniversalMailer.Api.Contracts.Admin;

public sealed class UpsertTemplateRequest
{
    public string DisplayName { get; set; } = string.Empty;

    public string Version { get; set; } = "1.0.0";

    public string Subject { get; set; } = string.Empty;

    public string BodyHtml { get; set; } = string.Empty;

    public string? Description { get; set; }

    public bool Ativo { get; set; } = true;
}

public sealed record TemplateResponse(
    string Chave,
    string Nome,
    string Versao,
    string Assunto,
    string CorpoHtml,
    string? Descricao,
    bool Ativo,
    DateTimeOffset CriadoEm,
    DateTimeOffset AtualizadoEm);
