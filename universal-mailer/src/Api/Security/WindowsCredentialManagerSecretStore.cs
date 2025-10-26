using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using UniversalMailer.Core.Security;

namespace UniversalMailer.Api.Security;

/// <summary>
/// Implementação baseada no Credential Manager do Windows com proteção DPAPI.
/// </summary>
public sealed class WindowsCredentialManagerSecretStore : ISecretStore
{
    private const string ReferencePrefix = "credential://";
    private readonly string _applicationName;

    public WindowsCredentialManagerSecretStore(string applicationName)
    {
        if (!OperatingSystem.IsWindows())
        {
            throw new PlatformNotSupportedException("O armazenamento seguro de segredos requer Windows.");
        }

        _applicationName = string.IsNullOrWhiteSpace(applicationName)
            ? throw new ArgumentException("Informe o nome lógico da aplicação para o Credential Manager.", nameof(applicationName))
            : applicationName.Trim();
    }

    public string StoreSecret(string name, string secret)
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            throw new ArgumentException("O nome do segredo é obrigatório.", nameof(name));
        }

        if (secret is null)
        {
            throw new ArgumentNullException(nameof(secret));
        }

        var sanitizedName = SanitizeName(name);
        var target = $"{_applicationName}/{sanitizedName}";
        var data = Protect(secret);

        var credential = new NativeCredential
        {
            AttributeCount = 0,
            Attributes = IntPtr.Zero,
            Comment = IntPtr.Zero,
            TargetAlias = IntPtr.Zero,
            Type = CredType.Generic,
            Persist = (uint)CredPersist.Enterprise,
            CredentialBlobSize = (uint)data.Length,
            Flags = 0
        };

        credential.TargetName = Marshal.StringToCoTaskMemUni(target);
        credential.UserName = Marshal.StringToCoTaskMemUni(Environment.UserName);
        credential.CredentialBlob = Marshal.AllocCoTaskMem(data.Length == 0 ? 1 : data.Length);
        if (data.Length > 0)
        {
            Marshal.Copy(data, 0, credential.CredentialBlob, data.Length);
        }

        try
        {
            if (!CredWrite(ref credential, 0))
            {
                throw new Win32Exception(Marshal.GetLastWin32Error(), "Não foi possível gravar o segredo no Credential Manager.");
            }

            return ReferencePrefix + target;
        }
        finally
        {
            if (data.Length > 0)
            {
                Array.Clear(data, 0, data.Length);
            }

            if (credential.CredentialBlob != IntPtr.Zero)
            {
                if (data.Length > 0)
                {
                    Marshal.Copy(new byte[data.Length], 0, credential.CredentialBlob, data.Length);
                }

                Marshal.FreeCoTaskMem(credential.CredentialBlob);
            }

            if (credential.TargetName != IntPtr.Zero)
            {
                Marshal.ZeroFreeCoTaskMemUnicode(credential.TargetName);
            }

            if (credential.UserName != IntPtr.Zero)
            {
                Marshal.ZeroFreeCoTaskMemUnicode(credential.UserName);
            }
        }
    }

    public string RetrieveSecret(string reference)
    {
        if (!IsReference(reference))
        {
            throw new ArgumentException("Referência inválida para o Credential Manager.", nameof(reference));
        }

        var target = reference[ReferencePrefix.Length..];
        if (!CredRead(target, CredType.Generic, 0, out var credentialPtr))
        {
            throw new Win32Exception(Marshal.GetLastWin32Error(), "Não foi possível recuperar o segredo do Credential Manager.");
        }

        try
        {
            var credential = Marshal.PtrToStructure<NativeCredential>(credentialPtr);
            if (credential is null)
            {
                throw new InvalidOperationException("Estrutura de credencial inválida retornada pelo sistema.");
            }

            if (credential.CredentialBlobSize == 0)
            {
                return string.Empty;
            }

            var buffer = new byte[credential.CredentialBlobSize];
            Marshal.Copy(credential.CredentialBlob, buffer, 0, buffer.Length);

            return Unprotect(buffer);
        }
        finally
        {
            CredFree(credentialPtr);
        }
    }

    public bool IsReference(string value)
        => !string.IsNullOrWhiteSpace(value)
           && value.StartsWith(ReferencePrefix, StringComparison.OrdinalIgnoreCase);

    private static string SanitizeName(string name)
    {
        var builder = new StringBuilder(name.Length);
        foreach (var ch in name)
        {
            if (char.IsLetterOrDigit(ch) || ch is '-' or '_' or '.' or '/')
            {
                builder.Append(ch);
            }
            else if (char.IsWhiteSpace(ch))
            {
                builder.Append('-');
            }
        }

        return builder.Length == 0 ? "secret" : builder.ToString();
    }

    private static byte[] Protect(string secret)
    {
        var data = Encoding.UTF8.GetBytes(secret);
        return ProtectedData.Protect(data, null, DataProtectionScope.CurrentUser);
    }

    private static string Unprotect(byte[] data)
    {
        var unprotected = ProtectedData.Unprotect(data, null, DataProtectionScope.CurrentUser);
        return Encoding.UTF8.GetString(unprotected);
    }

    [DllImport("Advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CredWrite(ref NativeCredential userCredential, uint flags);

    [DllImport("Advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CredRead(string target, CredType type, int reservedFlag, out IntPtr credentialPtr);

    [DllImport("Advapi32.dll", SetLastError = false)]
    private static extern void CredFree(IntPtr buffer);

    private enum CredType : uint
    {
        Generic = 1
    }

    private enum CredPersist : uint
    {
        Session = 1,
        LocalMachine,
        Enterprise
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private sealed class NativeCredential
    {
        public uint Flags;
        public CredType Type;
        public IntPtr TargetName;
        public IntPtr Comment;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWritten;
        public uint CredentialBlobSize;
        public IntPtr CredentialBlob;
        public uint Persist;
        public uint AttributeCount;
        public IntPtr Attributes;
        public IntPtr TargetAlias;
        public IntPtr UserName;
    }
}
