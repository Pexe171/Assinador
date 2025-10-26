using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows.Input;
using UniversalMailer.Client.Wpf.Infrastructure;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Engine.Services;

using MailAccountModel = UniversalMailer.Core.Mail.Models.MailAccount;

namespace UniversalMailer.Client.Wpf.ViewModels;

/// <summary>
/// ViewModel principal do formulário de envio.
/// </summary>
public sealed class SendMailViewModel : ObservableObject
{
    private readonly MailDispatcher _dispatcher;
    private readonly RelayCommand _previewCommand;
    private readonly RelayCommand _sendCommand;

    private string _nomeCliente = string.Empty;
    private string _cpf = string.Empty;
    private string _situacaoAtual = string.Empty;
    private string _urlPortal = string.Empty;
    private string _emailPara = string.Empty;
    private string _emailCc = string.Empty;
    private string _emailBcc = string.Empty;
    private string _valoresExtras = string.Empty;
    private string _previewHtml = string.Empty;
    private string _previewSubject = string.Empty;
    private string _statusMessage = string.Empty;
    private bool _isBusy;
    private DispatchAccountOption? _selectedAccount;
    private MailPreview? _lastPreview;
    private string? _lastPreviewSignature;

    public SendMailViewModel(MailDispatcher dispatcher, IEnumerable<DispatchAccountOption> accounts)
    {
        _dispatcher = dispatcher ?? throw new ArgumentNullException(nameof(dispatcher));

        Accounts = new ObservableCollection<DispatchAccountOption>(accounts ?? Array.Empty<DispatchAccountOption>());
        _selectedAccount = Accounts.FirstOrDefault();

        _previewCommand = new RelayCommand(() => _ = PreviewAsync(), CanPreview);
        _sendCommand = new RelayCommand(() => _ = SendAsync(), CanSend);
    }

    public ObservableCollection<DispatchAccountOption> Accounts { get; }

    public DispatchAccountOption? SelectedAccount
    {
        get => _selectedAccount;
        set
        {
            if (value == _selectedAccount)
            {
                return;
            }

            _selectedAccount = value;
            OnPropertyChanged();
            InvalidatePreview();
            RaiseCanExecuteChanged();
        }
    }

    public string NomeCliente
    {
        get => _nomeCliente;
        set
        {
            SetProperty(ref _nomeCliente, value);
            InvalidatePreview();
        }
    }

    public string Cpf
    {
        get => _cpf;
        set
        {
            SetProperty(ref _cpf, value);
            InvalidatePreview();
        }
    }

    public string SituacaoAtual
    {
        get => _situacaoAtual;
        set
        {
            SetProperty(ref _situacaoAtual, value);
            InvalidatePreview();
        }
    }

    public string UrlPortal
    {
        get => _urlPortal;
        set
        {
            SetProperty(ref _urlPortal, value);
            InvalidatePreview();
        }
    }

    public string EmailPara
    {
        get => _emailPara;
        set
        {
            SetProperty(ref _emailPara, value);
            InvalidatePreview();
        }
    }

    public string EmailCc
    {
        get => _emailCc;
        set
        {
            SetProperty(ref _emailCc, value);
            InvalidatePreview();
        }
    }

    public string EmailBcc
    {
        get => _emailBcc;
        set
        {
            SetProperty(ref _emailBcc, value);
            InvalidatePreview();
        }
    }

    public string ValoresExtras
    {
        get => _valoresExtras;
        set
        {
            SetProperty(ref _valoresExtras, value);
            InvalidatePreview();
        }
    }

    public string PreviewHtml
    {
        get => _previewHtml;
        private set => SetProperty(ref _previewHtml, value);
    }

    public string PreviewSubject
    {
        get => _previewSubject;
        private set => SetProperty(ref _previewSubject, value);
    }

    public string StatusMessage
    {
        get => _statusMessage;
        private set => SetProperty(ref _statusMessage, value);
    }

    public bool IsBusy
    {
        get => _isBusy;
        private set
        {
            SetProperty(ref _isBusy, value);
            RaiseCanExecuteChanged();
        }
    }

    public ICommand PreviewCommand => _previewCommand;

    public ICommand SendCommand => _sendCommand;

    private bool CanPreview() => !IsBusy && SelectedAccount is not null && !string.IsNullOrWhiteSpace(EmailPara);

    private bool CanSend()
        => !IsBusy
           && SelectedAccount is not null
           && _lastPreview is not null
           && string.Equals(_lastPreviewSignature, ComputeSignature(), StringComparison.Ordinal);

    private async Task PreviewAsync()
    {
        if (SelectedAccount is null)
        {
            StatusMessage = "Selecione uma conta antes de pré-visualizar.";
            return;
        }

        try
        {
            IsBusy = true;
            StatusMessage = "Gerando prévia...";

            var request = BuildRequest();
            _lastPreview = await _dispatcher.GeneratePreviewAsync(request).ConfigureAwait(false);
            _lastPreviewSignature = ComputeSignature();

            PreviewHtml = _lastPreview.BodyHtml;
            PreviewSubject = _lastPreview.Subject;
            StatusMessage = $"Prévia gerada com o identificador {_lastPreview.TrackingId}.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Erro ao gerar prévia: {ex.Message}";
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task SendAsync()
    {
        if (SelectedAccount is null)
        {
            StatusMessage = "Selecione uma conta antes de enviar.";
            return;
        }

        if (_lastPreview is null || !string.Equals(_lastPreviewSignature, ComputeSignature(), StringComparison.Ordinal))
        {
            StatusMessage = "A prévia ficou desatualizada. Gere novamente antes de enviar.";
            return;
        }

        try
        {
            IsBusy = true;
            StatusMessage = "Enviando e-mail...";

            var request = BuildRequest();
            var outcome = await _dispatcher.SendAsync(request, _lastPreview, SelectedAccount.Provider).ConfigureAwait(false);

            var sb = new StringBuilder();
            sb.Append("Envio concluído. MessageId: ");
            sb.Append(outcome.ProviderResult.MessageId);
            if (!string.IsNullOrWhiteSpace(outcome.ProviderResult.ThreadId))
            {
                sb.Append(" | ThreadId: ");
                sb.Append(outcome.ProviderResult.ThreadId);
            }

            StatusMessage = sb.ToString();
        }
        catch (Exception ex)
        {
            StatusMessage = $"Falha no envio: {ex.Message}";
        }
        finally
        {
            IsBusy = false;
        }
    }

    private MailDispatchRequest BuildRequest()
    {
        if (SelectedAccount is null)
        {
            throw new InvalidOperationException("Conta não selecionada.");
        }

        var to = ParseAddresses(EmailPara);
        if (to.Count == 0)
        {
            throw new InvalidOperationException("Informe ao menos um e-mail em 'Para'.");
        }

        var cc = ParseAddresses(EmailCc);
        var bcc = ParseAddresses(EmailBcc);

        var values = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["NOME"] = NomeCliente,
            ["CPF"] = Cpf,
            ["SITUACAO_ATUAL"] = SituacaoAtual,
            ["URL_PORTAL"] = UrlPortal
        };

        foreach (var (key, value) in ParseExtraValues())
        {
            values[key] = value;
        }

        return new MailDispatchRequest(SelectedAccount.Account, to, cc, bcc, values, templateKey: "validacao_renda");
    }

    private Dictionary<string, string> ParseExtraValues()
    {
        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        if (string.IsNullOrWhiteSpace(ValoresExtras))
        {
            return result;
        }

        using var reader = new StringReader(ValoresExtras);
        string? line;
        while ((line = reader.ReadLine()) is not null)
        {
            line = line.Trim();
            if (string.IsNullOrWhiteSpace(line))
            {
                continue;
            }

            var parts = line.Split('=', 2);
            if (parts.Length == 2)
            {
                result[parts[0].Trim()] = parts[1].Trim();
            }
        }

        return result;
    }

    private static List<MailAddress> ParseAddresses(string raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
        {
            return new List<MailAddress>();
        }

        var entries = raw
            .Split(new[] { ';', ',', '\n' }, StringSplitOptions.RemoveEmptyEntries)
            .Select(v => v.Trim())
            .Where(v => !string.IsNullOrWhiteSpace(v));

        return entries.Select(address => new MailAddress(address)).ToList();
    }

    private string ComputeSignature()
    {
        var builder = new StringBuilder();
        builder.Append(SelectedAccount?.Account.Id);
        builder.Append('|').Append(NomeCliente);
        builder.Append('|').Append(Cpf);
        builder.Append('|').Append(SituacaoAtual);
        builder.Append('|').Append(UrlPortal);
        builder.Append('|').Append(EmailPara);
        builder.Append('|').Append(EmailCc);
        builder.Append('|').Append(EmailBcc);
        builder.Append('|').Append(ValoresExtras);
        return builder.ToString();
    }

    private void InvalidatePreview()
    {
        _lastPreviewSignature = null;
        RaiseCanExecuteChanged();
    }

    private void RaiseCanExecuteChanged()
    {
        _previewCommand.RaiseCanExecuteChanged();
        _sendCommand.RaiseCanExecuteChanged();
    }
}

/// <summary>
/// Vincula a conta de envio ao provedor selecionado.
/// </summary>
public sealed record DispatchAccountOption(MailAccountModel Account, IMailProvider Provider)
{
    public override string ToString() => Account.DisplayName;
}
