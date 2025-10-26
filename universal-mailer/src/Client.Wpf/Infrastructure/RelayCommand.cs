using System.Windows.Input;

namespace UniversalMailer.Client.Wpf.Infrastructure;

/// <summary>
/// Implementação simples de ICommand para facilitar o binding no MVVM.
/// </summary>
public sealed class RelayCommand : ICommand
{
    private readonly Func<bool>? _canExecute;
    private readonly Action _execute;

    public RelayCommand(Action execute, Func<bool>? canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;

    public void Execute(object? parameter) => _execute();

    public event EventHandler? CanExecuteChanged;

    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
