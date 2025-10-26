using UniversalMailer.Core.Returns.Contracts;
using UniversalMailer.Core.Returns.Models;

namespace UniversalMailer.Core.Returns.Processing;

/// <summary>
/// Coordena extração de ID, classificação e persistência dos retornos recebidos.
/// </summary>
public sealed class ReturnMessageProcessor
{
    private readonly IReturnClassifier _classifier;
    private readonly IReturnStore _store;

    public ReturnMessageProcessor(
        IReturnClassifier classifier,
        IReturnStore store)
    {
        _classifier = classifier ?? throw new ArgumentNullException(nameof(classifier));
        _store = store ?? throw new ArgumentNullException(nameof(store));
    }

    public async Task<ReturnProcessingResult> ProcessAsync(ReturnMessage message, CancellationToken cancellationToken = default)
    {
        if (message is null)
        {
            throw new ArgumentNullException(nameof(message));
        }

        cancellationToken.ThrowIfCancellationRequested();

        var normalizedSubject = ReturnTextSanitizer.Normalize(message.Subject);
        var normalizedBody = ReturnTextSanitizer.Normalize(message.Body);

        var trackingId = ReturnTrackingIdExtractor.Extract(normalizedSubject, normalizedBody);
        var hasValidTrackingId = !string.IsNullOrWhiteSpace(trackingId);
        var trackingKey = hasValidTrackingId ? trackingId! : $"MANUAL-{message.ProviderMessageId}";

        var existingThread = await _store.GetAsync(trackingKey, cancellationToken).ConfigureAwait(false);

        var classification = await _classifier
            .ClassifyAsync(message with
            {
                Subject = normalizedSubject,
                Body = normalizedBody
            }, cancellationToken)
            .ConfigureAwait(false);

        if (!hasValidTrackingId)
        {
            classification = classification.WithStatus(
                ReturnStatus.Manual,
                new[] { "Identificador AC-#### não encontrado no assunto/corpo." },
                true);
        }
        else if (existingThread is not null)
        {
            classification = ReturnClassification.Duplicate(trackingKey, existingThread.Messages.Count + 1);
        }

        var record = new ReturnRecord(
            trackingKey,
            hasValidTrackingId,
            message.ProviderMessageId,
            message.AccountId,
            message.ProviderType,
            message.Sender,
            normalizedSubject,
            ReturnTextSanitizer.BuildPreview(normalizedBody),
            classification,
            message.ReceivedAt,
            message.ConversationId,
            message.Metadata);

        var thread = await _store.SaveAsync(record, cancellationToken).ConfigureAwait(false);

        return new ReturnProcessingResult(
            record,
            thread,
            existingThread is null,
            classification.Status == ReturnStatus.Duplo);
    }
}
