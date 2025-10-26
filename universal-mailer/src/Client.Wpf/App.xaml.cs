using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Windows;
using System.Windows.Threading;
using UniversalMailer.Client.Wpf.ViewModels;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Engine.Services;
using UniversalMailer.Engine.Templates;
using UniversalMailer.Mail.Adapters.FileSystem;
using UniversalMailer.Persistence.Stores;

namespace UniversalMailer.Client.Wpf;

public partial class App : Application
{
    private static readonly string ErrorLogPath = Path.Combine(AppContext.BaseDirectory, "client-wpf-errors.log");

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        DispatcherUnhandledException += OnDispatcherUnhandledException;

        try
        {
            InitializeShell();
        }
        catch (Exception ex)
        {
            HandleFatalStartupException("Não foi possível iniciar a aplicação.", ex);
        }
    }

    private void InitializeShell()
    {
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

    private void OnDispatcherUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs e)
    {
        var logPath = LogException("Exceção não tratada no Dispatcher", e.Exception);

        var message = new StringBuilder();
        message.AppendLine("Ocorreu um erro inesperado e o aplicativo será encerrado.");
        message.AppendLine();
        message.AppendLine(e.Exception.Message);

        if (!string.IsNullOrWhiteSpace(logPath))
        {
            message.AppendLine();
            message.AppendLine("Detalhes adicionais foram gravados em:");
            message.AppendLine(logPath);
        }

        MessageBox.Show(message.ToString(), "Erro inesperado", MessageBoxButton.OK, MessageBoxImage.Error);
        e.Handled = true;
        Shutdown(-1);
    }

    private void HandleFatalStartupException(string context, Exception exception)
    {
        var logPath = LogException(context, exception);

        var message = new StringBuilder();
        message.AppendLine(context);
        message.AppendLine();
        message.AppendLine(exception.Message);

        if (!string.IsNullOrWhiteSpace(logPath))
        {
            message.AppendLine();
            message.AppendLine("Detalhes adicionais foram gravados em:");
            message.AppendLine(logPath);
        }

        MessageBox.Show(message.ToString(), "Erro ao iniciar", MessageBoxButton.OK, MessageBoxImage.Error);
        Shutdown(-1);
    }

    private static string LogException(string context, Exception exception)
    {
        try
        {
            var directory = Path.GetDirectoryName(ErrorLogPath);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            var builder = new StringBuilder();
            builder.AppendLine($"[{DateTimeOffset.Now:O}] {context}");
            builder.AppendLine(exception.ToString());
            builder.AppendLine(new string('-', 80));

            File.AppendAllText(ErrorLogPath, builder.ToString());
            return ErrorLogPath;
        }
        catch
        {
            return string.Empty;
        }
    }

    private static IReadOnlyCollection<DispatchAccountOption> LoadAccounts(string configPath, string baseDirectory)
    {
        var resolvedConfigPath = EnsureConfigFile(configPath, baseDirectory);

        var json = File.ReadAllText(resolvedConfigPath);
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

    private static string EnsureConfigFile(string configPath, string baseDirectory)
    {
        if (File.Exists(configPath))
        {
            return configPath;
        }

        var fallbackPath = ResolvePath(baseDirectory, Path.Combine("..", "..", "..", "..", "..", "config", "mail.providers.json"));
        if (File.Exists(fallbackPath))
        {
            try
            {
                var targetDirectory = Path.GetDirectoryName(configPath);
                if (!string.IsNullOrWhiteSpace(targetDirectory))
                {
                    Directory.CreateDirectory(targetDirectory);
                }

                File.Copy(fallbackPath, configPath, overwrite: false);

                if (File.Exists(configPath))
                {
                    return configPath;
                }
            }
            catch (IOException)
            {
                // Ignorado: se não conseguir copiar, continua usando o caminho original.
            }
            catch (UnauthorizedAccessException)
            {
                // Ignorado: sem permissão para copiar, usa o arquivo de origem diretamente.
            }

            return fallbackPath;
        }

        var message = new StringBuilder();
        message.AppendLine($"Arquivo de configuração de contas não encontrado: {configPath}");
        message.Append($"Também foi verificado o caminho alternativo: {fallbackPath}");

        throw new FileNotFoundException(message.ToString());
    }

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
