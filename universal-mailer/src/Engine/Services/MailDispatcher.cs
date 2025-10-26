using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Core.Mail.Policies;
using UniversalMailer.Core.Mail.Records;
using UniversalMailer.Engine.Templates;
using UniversalMailer.Engine.Utils;
using MailEnvelopeModel = UniversalMailer.Core.Mail.Models.MailEnvelope;

namespace UniversalMailer.Engine.Services;

/// <summary>
/// Coordena a prévia obrigatória e o envio efetivo sem alterar os dados informados pela operação.
/// </summary>
public sealed class MailDispatcher
{
    private readonly ITemplateRepository _templateRepository;
    private readonly TemplateRenderer _renderer;
    private readonly IMailDispatchStore _dispatchStore;
    private readonly IMailRecipientPolicy _recipientPolicy;

    public MailDispatcher(
        ITemplateRepository templateRepository,
        TemplateRenderer renderer,
        IMailDispatchStore dispatchStore,
        IMailRecipientPolicy recipientPolicy)
    {
        _templateRepository = templateRepository ?? throw new ArgumentNullException(nameof(templateRepository));
        _renderer = renderer ?? throw new ArgumentNullException(nameof(renderer));
        _dispatchStore = dispatchStore ?? throw new ArgumentNullException(nameof(dispatchStore));
        _recipientPolicy = recipientPolicy ?? throw new ArgumentNullException(nameof(recipientPolicy));
    }

    public async Task<MailPreview> GeneratePreviewAsync(MailDispatchRequest request, CancellationToken cancellationToken = default)
    {
        if (request is null)
        {
            throw new ArgumentNullException(nameof(request));
        }

        var template = await _templateRepository.GetAsync(request.TemplateKey, cancellationToken).ConfigureAwait(false);
        var trackingId = TrackingIdGenerator.Create();
        var values = CreateValueMap(request.Values, trackingId);

        var subject = _renderer.RenderSubject(template, values);
        var body = await _renderer.RenderBodyAsync(template, values, cancellationToken).ConfigureAwait(false);

        return new MailPreview(trackingId, subject, body, template.Version);
    }

    public async Task<MailDispatchOutcome> SendAsync(
        MailDispatchRequest request,
        MailPreview preview,
        IMailProvider provider,
        CancellationToken cancellationToken = default)
    {
        if (request is null)
        {
            throw new ArgumentNullException(nameof(request));
        }

        if (preview is null)
        {
            throw new ArgumentNullException(nameof(preview));
        }

        if (provider is null)
        {
            throw new ArgumentNullException(nameof(provider));
        }

        var sanitized = _recipientPolicy.Apply(request.To, request.Cc, request.Bcc);
        var envelope = new MailEnvelopeModel(sanitized.To, sanitized.Cc, sanitized.Bcc);
        var content = new MailContent(preview.Subject, preview.BodyHtml);
        var sendRequest = new MailSendRequest(request.Account, envelope, content, preview.TrackingId);

        var result = await provider.SendAsync(sendRequest, cancellationToken).ConfigureAwait(false);

        var record = new MailDispatchRecord(
            preview.TrackingId,
            request.TemplateKey,
            preview.TemplateVersion,
            request.Account,
            envelope,
            result,
            DateTimeOffset.UtcNow);

        await _dispatchStore.SaveAsync(record, cancellationToken).ConfigureAwait(false);

        return new MailDispatchOutcome(result, record);
    }

    private static Dictionary<string, string> CreateValueMap(
        IReadOnlyDictionary<string, string> original,
        string trackingId)
    {
        var comparer = StringComparer.OrdinalIgnoreCase;
        var values = new Dictionary<string, string>(original, comparer)
        {
            ["ID"] = trackingId
        };

        return values;
    }
}
