using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Windows;
using UniversalMailer.Client.Wpf.ViewModels;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Engine.Services;
using UniversalMailer.Engine.Templates;
using UniversalMailer.Mail.Adapters.FileSystem;
using UniversalMailer.Persistence.Stores;

namespace UniversalMailer.Client.Wpf;

public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        var baseDirectory = AppContext.BaseDirectory;
        var manifestPath = Path.Combine(baseDirectory, "templates.json");
        var templateDirectory = baseDirectory;
        var configPath = Path.Combine(baseDirectory, "mail.providers.json");
        var logPath = ResolvePath(baseDirectory, Path.Combine("..", "..", "..", "..", "..", "db", "mail-dispatch-log.jsonl"));

        var templateRepository = new JsonTemplateRepository(manifestPath);
        var renderer = new TemplateRenderer(templateDirectory);
        var dispatchStore = new FileMailDispatchStore(logPath);
        var dispatcher = new MailDispatcher(templateRepository, renderer, dispatchStore);

        var accounts = LoadAccounts(configPath, baseDirectory);
        var viewModel = new SendMailViewModel(dispatcher, accounts);

        var window = new Views.MainWindow
        {
            DataContext = viewModel
        };

        window.Show();
    }

    private static IReadOnlyCollection<DispatchAccountOption> LoadAccounts(string configPath, string baseDirectory)
    {
        if (!File.Exists(configPath))
        {
            throw new FileNotFoundException($"Arquivo de configuração de contas não encontrado: {configPath}");
        }

        var json = File.ReadAllText(configPath);
        var payload = JsonSerializer.Deserialize<MailProviderConfig>(json, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        }) ?? throw new InvalidOperationException("Não foi possível carregar o arquivo de contas de e-mail.");

        var accounts = new List<DispatchAccountOption>();
        foreach (var account in payload.Accounts)
        {
            if (!string.Equals(account.Provider, "filesystem", StringComparison.OrdinalIgnoreCase))
            {
                throw new NotSupportedException($"Provedor '{account.Provider}' ainda não suportado nesta interface.");
            }

            if (account.Options?.OutboxDirectory is null)
            {
                throw new InvalidOperationException($"Conta '{account.Id}' sem diretório de saída configurado.");
            }

            var outboxPath = ResolvePath(baseDirectory, account.Options.OutboxDirectory);
            var provider = new FileSystemMailProvider(new FileSystemMailProviderOptions
            {
                OutboxDirectory = outboxPath,
                DefaultThreadId = account.Options.DefaultThreadId
            });

            accounts.Add(new DispatchAccountOption(new MailAccount(account.Id, account.DisplayName ?? account.Id), provider));
        }

        return accounts;
    }

    private static string ResolvePath(string baseDirectory, string relativePath)
        => Path.GetFullPath(Path.Combine(baseDirectory, relativePath));

    private sealed class MailProviderConfig
    {
        public List<MailAccountConfig> Accounts { get; set; } = new();
    }

    private sealed class MailAccountConfig
    {
        public string Id { get; set; } = string.Empty;

        public string? DisplayName { get; set; }

        public string Provider { get; set; } = string.Empty;

        public MailProviderOptions? Options { get; set; }
    }

    private sealed class MailProviderOptions
    {
        public string? OutboxDirectory { get; set; }

        public string? DefaultThreadId { get; set; }
    }
}
