namespace UniversalMailer.Api.Infrastructure;

public sealed class DatabaseOptions
{
    public string Provider { get; set; } = "sqlite";

    public string ConnectionString { get; set; } = string.Empty;
}
