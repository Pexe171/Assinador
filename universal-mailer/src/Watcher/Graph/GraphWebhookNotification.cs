namespace UniversalMailer.Watcher.Graph;

/// <summary>
/// Representa uma notificação recebida pelo webhook do Microsoft Graph.
/// </summary>
public sealed record GraphWebhookNotification(
    string AccountId,
    string MessageId,
    string SubscriptionId,
    DateTimeOffset ReceivedAt);
