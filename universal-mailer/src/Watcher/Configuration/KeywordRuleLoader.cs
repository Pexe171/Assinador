using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Core.Returns.Processing;

namespace UniversalMailer.Watcher.Configuration;

/// <summary>
/// Carrega regras de palavras-chave a partir de um arquivo YAML simples.
/// </summary>
public static class KeywordRuleLoader
{
    public static IReadOnlyDictionary<ReturnStatus, IReadOnlyCollection<KeywordRule>> LoadFromYaml(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            throw new ArgumentException("O caminho do arquivo é obrigatório.", nameof(path));
        }

        if (!File.Exists(path))
        {
            throw new FileNotFoundException($"Arquivo de palavras-chave não encontrado: {path}", path);
        }

        var rules = new Dictionary<ReturnStatus, List<KeywordRule>>();
        ReturnStatus? currentStatus = null;

        var lines = File.ReadAllLines(path);
        foreach (var rawLine in lines)
        {
            var line = rawLine.Trim();
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#", StringComparison.Ordinal))
            {
                continue;
            }

            if (!rawLine.StartsWith(" ") && line.EndsWith(":", StringComparison.Ordinal))
            {
                var statusName = line[..^1];
                if (!Enum.TryParse(statusName, true, out ReturnStatus status))
                {
                    throw new FormatException($"Status de retorno desconhecido: '{statusName}'.");
                }

                currentStatus = status;
                if (!rules.ContainsKey(status))
                {
                    rules[status] = new List<KeywordRule>();
                }
                continue;
            }

            if (currentStatus is null)
            {
                throw new FormatException("Arquivo YAML inválido: palavra-chave listada antes da definição do status.");
            }

            var keyword = line.TrimStart('-').Trim().Trim('"');
            if (!string.IsNullOrWhiteSpace(keyword))
            {
                rules[currentStatus.Value].Add(new KeywordRule(keyword));
            }
        }

        return rules.ToDictionary(
            pair => pair.Key,
            pair => (IReadOnlyCollection<KeywordRule>)pair.Value.AsReadOnly());
    }
}
