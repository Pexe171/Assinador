using System.Security.Cryptography;

namespace UniversalMailer.Engine.Utils;

/// <summary>
/// Gera identificadores com o padrão AC-####, garantindo baixa colisão.
/// </summary>
public static class TrackingIdGenerator
{
    public static string Create()
    {
        Span<byte> buffer = stackalloc byte[2];
        RandomNumberGenerator.Fill(buffer);
        var number = BitConverter.ToUInt16(buffer);
        var suffix = (number % 10000).ToString("D4");
        return $"AC-{suffix}";
    }
}
