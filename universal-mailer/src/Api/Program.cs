using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using Microsoft.OpenApi.Models;
using UniversalMailer.Api.Contracts.Admin;
using UniversalMailer.Api.Contracts.Emails;
using UniversalMailer.Api.Contracts.Returns;
using UniversalMailer.Api.Contracts.Search;
using UniversalMailer.Api.Infrastructure;
using UniversalMailer.Api.Services;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Mail.Models;
using UniversalMailer.Core.Returns.Contracts;
using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Engine.Services;
using UniversalMailer.Engine.Templates;
using UniversalMailer.Mail.Adapters.Common;
using UniversalMailer.Mail.Adapters.FileSystem;
using UniversalMailer.Persistence.Db;
using UniversalMailer.Persistence.Entities;
using UniversalMailer.Persistence.Stores;

var builder = WebApplication.CreateBuilder(args);

builder.Services.Configure<DatabaseOptions>(builder.Configuration.GetSection("Database"));

builder.Services.AddDbContext<MailerDbContext>((serviceProvider, options) =>
{
    var database = serviceProvider.GetRequiredService<IOptions<DatabaseOptions>>().Value;
    if (string.Equals(database.Provider, "postgres", StringComparison.OrdinalIgnoreCase))
    {
        options.UseNpgsql(database.ConnectionString);
    }
    else
    {
        options.UseSqlite(database.ConnectionString);
    }
});

builder.Services.AddScoped<IMailDispatchStore, EfMailDispatchStore>();
builder.Services.AddScoped<IReturnStore, EfReturnStore>();
builder.Services.AddScoped<ITemplateRepository, EfTemplateRepository>();
builder.Services.AddScoped<TemplateRenderer>(_ => new TemplateRenderer(builder.Configuration.GetValue<string>("Templates:Directory") ?? "templates"));
builder.Services.AddScoped<MailDispatcher>();
builder.Services.AddScoped<DispatchContextFactory>();
builder.Services.AddScoped<SearchService>();

builder.Services.AddSingleton(sp =>
{
    var factories = new Dictionary<MailProviderType, Func<MailProviderDescriptor, IMailProvider>>
    {
        [MailProviderType.FileSystem] = descriptor =>
        {
            if (!descriptor.Settings.TryGetValue("outboxDirectory", out var directory) || string.IsNullOrWhiteSpace(directory))
            {
                throw new InvalidOperationException("A configuração 'outboxDirectory' é obrigatória para o provedor FileSystem.");
            }

            descriptor.Settings.TryGetValue("defaultThreadId", out var defaultThreadId);

            return new FileSystemMailProvider(new FileSystemMailProviderOptions
            {
                OutboxDirectory = directory,
                DefaultThreadId = string.IsNullOrWhiteSpace(defaultThreadId) ? null : defaultThreadId
            });
        }
    };

    return new MailProviderRegistry(factories);
});

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Universal Mailer API",
        Version = "v1",
        Description = "Endpoints REST para orquestração de envios, retornos e cadastros administrativos."
    });
});

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<MailerDbContext>();
    context.Database.Migrate();
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

var emails = app.MapGroup("/emails");

emails.MapPost("/send", async Task<Results<Ok<SendEmailResponse>, BadRequest<IDictionary<string, string>>>> (
    SendEmailRequest request,
    MailDispatcher dispatcher,
    DispatchContextFactory dispatchContextFactory,
    CancellationToken cancellationToken) =>
{
    if (request is null)
    {
        return TypedResults.BadRequest(new Dictionary<string, string> { ["erro"] = "Payload inválido." });
    }

    if (request.Para.Count == 0)
    {
        return TypedResults.BadRequest(new Dictionary<string, string> { ["erro"] = "Informe ao menos um destinatário em 'para'." });
    }

    try
    {
        var context = await dispatchContextFactory.CreateAsync(request.AccountId, cancellationToken).ConfigureAwait(false);
        var to = request.Para.Select(MapAddress).ToArray();
        var cc = request.Cc.Select(MapAddress).ToArray();
        var bcc = request.Bcc.Select(MapAddress).ToArray();

        var dispatchRequest = new MailDispatchRequest(
            context.Account,
            to,
            cc,
            bcc,
            request.Variaveis,
            request.TemplateKey);

        var preview = await dispatcher.GeneratePreviewAsync(dispatchRequest, cancellationToken).ConfigureAwait(false);
        var outcome = await dispatcher.SendAsync(dispatchRequest, preview, context.Provider, cancellationToken).ConfigureAwait(false);

        var response = new SendEmailResponse(
            preview.TrackingId,
            outcome.ProviderResult.MessageId,
            outcome.ProviderResult.ThreadId,
            outcome.ProviderResult.SentAt);

        return TypedResults.Ok(response);
    }
    catch (Exception ex) when (ex is ArgumentException or InvalidOperationException)
    {
        return TypedResults.BadRequest(new Dictionary<string, string> { ["erro"] = ex.Message });
    }
});

emails.MapGet("/{protocolo}", async Task<Results<Ok<EmailDetailsResponse>, NotFound>> (
    string protocolo,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var entity = await db.MailDispatches
        .AsNoTracking()
        .Include(dispatch => dispatch.Recipients)
        .FirstOrDefaultAsync(dispatch => dispatch.TrackingId == protocolo, cancellationToken)
        .ConfigureAwait(false);

    if (entity is null)
    {
        return TypedResults.NotFound();
    }

    var account = new EmailAccountSummary(entity.AccountId, entity.AccountName);
    var destinatarios = entity.Recipients
        .OrderBy(recipient => recipient.Type)
        .Select(recipient => new EmailRecipientSummary(recipient.Type.ToString(), recipient.Email, recipient.Name))
        .ToArray();

    var response = new EmailDetailsResponse(
        entity.TrackingId,
        entity.TemplateKey,
        entity.TemplateVersion,
        account,
        entity.ProviderMessageId,
        entity.ProviderThreadId,
        entity.SentAt,
        entity.LoggedAt,
        destinatarios);

    return TypedResults.Ok(response);
});

var returnsGroup = app.MapGroup("/returns");

returnsGroup.MapGet("/{protocolo}", async Task<Results<Ok<ReturnThreadResponse>, NotFound>> (
    string protocolo,
    IReturnStore store,
    CancellationToken cancellationToken) =>
{
    var thread = await store.GetAsync(protocolo, cancellationToken).ConfigureAwait(false);
    if (thread is null)
    {
        return TypedResults.NotFound();
    }

    var mensagens = thread.Messages.Select(message => new ReturnMessageResponse(
        message.ProviderMessageId,
        message.AccountId,
        message.ProviderType.ToString(),
        message.Sender.Address,
        message.Sender.Name,
        message.Subject,
        message.BodyPreview,
        message.Status.ToString(),
        message.Classification.Score,
        message.Classification.MatchedKeywords.ToArray(),
        message.Classification.Reasons.ToArray(),
        message.Classification.RequiresManualReview,
        message.ReceivedAt,
        message.ConversationId,
        message.Metadata ?? new Dictionary<string, string>())).ToArray();

    var response = new ReturnThreadResponse(
        thread.TrackingKey,
        thread.HasValidTrackingId,
        thread.SlaStatus.ToString(),
        thread.SlaStatusChangedAt,
        thread.CreatedAt,
        thread.UpdatedAt,
        thread.LastFollowUpAt,
        mensagens);

    return TypedResults.Ok(response);
});

app.MapGet("/search", async Task<SearchResponse> (
    string? protocolo,
    string? email,
    string? status,
    SearchService service,
    CancellationToken cancellationToken) =>
{
    return await service.SearchAsync(protocolo, email, status, cancellationToken).ConfigureAwait(false);
});

var admin = app.MapGroup("/admin");
var templates = admin.MapGroup("/templates");

templates.MapGet("/", async Task<IReadOnlyCollection<TemplateResponse>> (
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var templates = await db.Templates
        .AsNoTracking()
        .OrderBy(template => template.DisplayName)
        .ToListAsync(cancellationToken)
        .ConfigureAwait(false);

    return templates.Select(MapTemplate).ToList();
});

templates.MapGet("/{key}", async Task<Results<Ok<TemplateResponse>, NotFound>> (
    string key,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var template = await db.Templates
        .AsNoTracking()
        .FirstOrDefaultAsync(entity => entity.Key == key, cancellationToken)
        .ConfigureAwait(false);

    return template is null
        ? TypedResults.NotFound()
        : TypedResults.Ok(MapTemplate(template));
});

templates.MapPost("/{key}", async Task<Results<Created<TemplateResponse>, BadRequest<IDictionary<string, string>>>> (
    string key,
    UpsertTemplateRequest request,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    if (string.IsNullOrWhiteSpace(key))
    {
        return TypedResults.BadRequest(new Dictionary<string, string> { ["erro"] = "A chave do template é obrigatória." });
    }

    var exists = await db.Templates.AnyAsync(entity => entity.Key == key, cancellationToken).ConfigureAwait(false);
    if (exists)
    {
        return TypedResults.BadRequest(new Dictionary<string, string> { ["erro"] = "Já existe um template com essa chave." });
    }

    var now = DateTimeOffset.UtcNow;
    var entity = new TemplateEntity
    {
        Id = Guid.NewGuid(),
        Key = key,
        DisplayName = request.DisplayName,
        Version = request.Version,
        Subject = request.Subject,
        Body = request.BodyHtml,
        Description = request.Description,
        IsActive = request.Ativo,
        CreatedAt = now,
        UpdatedAt = now
    };

    db.Templates.Add(entity);
    await db.SaveChangesAsync(cancellationToken).ConfigureAwait(false);

    return TypedResults.Created($"/admin/templates/{key}", MapTemplate(entity));
});

templates.MapPut("/{key}", async Task<Results<Ok<TemplateResponse>, NotFound>> (
    string key,
    UpsertTemplateRequest request,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var entity = await db.Templates.FirstOrDefaultAsync(template => template.Key == key, cancellationToken).ConfigureAwait(false);
    if (entity is null)
    {
        return TypedResults.NotFound();
    }

    entity.DisplayName = request.DisplayName;
    entity.Version = request.Version;
    entity.Subject = request.Subject;
    entity.Body = request.BodyHtml;
    entity.Description = request.Description;
    entity.IsActive = request.Ativo;
    entity.UpdatedAt = DateTimeOffset.UtcNow;

    await db.SaveChangesAsync(cancellationToken).ConfigureAwait(false);

    return TypedResults.Ok(MapTemplate(entity));
});

templates.MapDelete("/{key}", async Task<Results<NoContent, NotFound>> (
    string key,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var entity = await db.Templates.FirstOrDefaultAsync(template => template.Key == key, cancellationToken).ConfigureAwait(false);
    if (entity is null)
    {
        return TypedResults.NotFound();
    }

    db.Templates.Remove(entity);
    await db.SaveChangesAsync(cancellationToken).ConfigureAwait(false);

    return TypedResults.NoContent();
});

var providers = admin.MapGroup("/providers");

providers.MapGet("/", async Task<IReadOnlyCollection<ProviderResponse>> (
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var entities = await db.MailProviders
        .AsNoTracking()
        .Include(provider => provider.Accounts)
        .OrderBy(provider => provider.DisplayName)
        .ToListAsync(cancellationToken)
        .ConfigureAwait(false);

    return entities.Select(MapProvider).ToList();
});

providers.MapGet("/{id:guid}", async Task<Results<Ok<ProviderResponse>, NotFound>> (
    Guid id,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var entity = await db.MailProviders
        .AsNoTracking()
        .Include(provider => provider.Accounts)
        .FirstOrDefaultAsync(provider => provider.Id == id, cancellationToken)
        .ConfigureAwait(false);

    return entity is null
        ? TypedResults.NotFound()
        : TypedResults.Ok(MapProvider(entity));
});

providers.MapPost("/", async Task<Results<Created<ProviderResponse>, BadRequest<IDictionary<string, string>>>> (
    UpsertProviderRequest request,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    if (string.IsNullOrWhiteSpace(request.Name))
    {
        return TypedResults.BadRequest(new Dictionary<string, string> { ["erro"] = "O nome interno do provedor é obrigatório." });
    }

    var exists = await db.MailProviders.AnyAsync(provider => provider.Name == request.Name, cancellationToken).ConfigureAwait(false);
    if (exists)
    {
        return TypedResults.BadRequest(new Dictionary<string, string> { ["erro"] = "Já existe um provedor com esse nome interno." });
    }

    var entity = CreateProviderEntity(request);
    db.MailProviders.Add(entity);
    await db.SaveChangesAsync(cancellationToken).ConfigureAwait(false);

    return TypedResults.Created($"/admin/providers/{entity.Id}", MapProvider(entity));
});

providers.MapPut("/{id:guid}", async Task<Results<Ok<ProviderResponse>, NotFound>> (
    Guid id,
    UpsertProviderRequest request,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var entity = await db.MailProviders
        .Include(provider => provider.Accounts)
        .FirstOrDefaultAsync(provider => provider.Id == id, cancellationToken)
        .ConfigureAwait(false);

    if (entity is null)
    {
        return TypedResults.NotFound();
    }

    entity.Name = request.Name;
    entity.DisplayName = request.DisplayName;
    entity.Type = request.Tipo;
    entity.SettingsJson = JsonHelpers.SerializeDictionary(request.Configuracoes);
    entity.IsActive = request.Ativo;
    entity.UpdatedAt = DateTimeOffset.UtcNow;

    SynchronizeAccounts(entity, request.Contas);

    await db.SaveChangesAsync(cancellationToken).ConfigureAwait(false);

    return TypedResults.Ok(MapProvider(entity));
});

providers.MapDelete("/{id:guid}", async Task<Results<NoContent, NotFound>> (
    Guid id,
    MailerDbContext db,
    CancellationToken cancellationToken) =>
{
    var entity = await db.MailProviders.FirstOrDefaultAsync(provider => provider.Id == id, cancellationToken).ConfigureAwait(false);
    if (entity is null)
    {
        return TypedResults.NotFound();
    }

    db.MailProviders.Remove(entity);
    await db.SaveChangesAsync(cancellationToken).ConfigureAwait(false);

    return TypedResults.NoContent();
});

app.Run();

static MailAddress MapAddress(EmailRecipientInput input)
    => new(input.Email, input.Nome);

static TemplateResponse MapTemplate(TemplateEntity entity)
    => new(
        entity.Key,
        entity.DisplayName,
        entity.Version,
        entity.Subject,
        entity.Body,
        entity.Description,
        entity.IsActive,
        entity.CreatedAt,
        entity.UpdatedAt);

static ProviderResponse MapProvider(MailProviderEntity entity)
{
    var contas = entity.Accounts
        .OrderBy(account => account.AccountId)
        .Select(account => new AccountResponse(
            account.Id,
            account.AccountId,
            account.Address,
            string.IsNullOrWhiteSpace(account.DisplayName) ? account.Address : account.DisplayName!,
            JsonHelpers.DeserializeDictionary(account.MetadataJson),
            account.IsActive,
            account.CreatedAt,
            account.UpdatedAt))
        .ToList();

    return new ProviderResponse(
        entity.Id,
        entity.Name,
        entity.DisplayName,
        entity.Type.ToString(),
        JsonHelpers.DeserializeDictionary(entity.SettingsJson),
        entity.IsActive,
        entity.CreatedAt,
        entity.UpdatedAt,
        contas);
}

static MailProviderEntity CreateProviderEntity(UpsertProviderRequest request)
{
    var now = DateTimeOffset.UtcNow;
    var provider = new MailProviderEntity
    {
        Id = Guid.NewGuid(),
        Name = request.Name,
        DisplayName = request.DisplayName,
        Type = request.Tipo,
        SettingsJson = JsonHelpers.SerializeDictionary(request.Configuracoes),
        IsActive = request.Ativo,
        CreatedAt = now,
        UpdatedAt = now,
        Accounts = new List<MailAccountEntity>()
    };

    foreach (var account in request.Contas)
    {
        provider.Accounts.Add(new MailAccountEntity
        {
            Id = Guid.NewGuid(),
            AccountId = account.AccountId,
            Address = account.Address,
            DisplayName = account.DisplayName,
            MetadataJson = JsonHelpers.SerializeDictionary(account.Metadata),
            IsActive = account.Ativo,
            CreatedAt = now,
            UpdatedAt = now
        });
    }

    return provider;
}

static void SynchronizeAccounts(MailProviderEntity provider, IReadOnlyCollection<UpsertAccountRequest> requests)
{
    var now = DateTimeOffset.UtcNow;
    var existingByAccountId = provider.Accounts.ToDictionary(account => account.AccountId, StringComparer.OrdinalIgnoreCase);

    foreach (var request in requests)
    {
        if (existingByAccountId.TryGetValue(request.AccountId, out var entity))
        {
            entity.Address = request.Address;
            entity.DisplayName = request.DisplayName;
            entity.MetadataJson = JsonHelpers.SerializeDictionary(request.Metadata);
            entity.IsActive = request.Ativo;
            entity.UpdatedAt = now;
        }
        else
        {
            provider.Accounts.Add(new MailAccountEntity
            {
                Id = Guid.NewGuid(),
                AccountId = request.AccountId,
                Address = request.Address,
                DisplayName = request.DisplayName,
                MetadataJson = JsonHelpers.SerializeDictionary(request.Metadata),
                IsActive = request.Ativo,
                CreatedAt = now,
                UpdatedAt = now
            });
        }
    }

    var toRemove = provider.Accounts.Where(account => requests.All(request => !request.AccountId.Equals(account.AccountId, StringComparison.OrdinalIgnoreCase))).ToList();
    foreach (var remove in toRemove)
    {
        provider.Accounts.Remove(remove);
    }
}
