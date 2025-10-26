using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Persistence.Entities;

namespace UniversalMailer.Persistence.Db;

public sealed class MailerDbContext : DbContext
{
    public MailerDbContext(DbContextOptions<MailerDbContext> options) : base(options)
    {
    }

    public DbSet<MailDispatchEntity> MailDispatches => Set<MailDispatchEntity>();

    public DbSet<MailRecipientEntity> MailRecipients => Set<MailRecipientEntity>();

    public DbSet<ReturnThreadEntity> ReturnThreads => Set<ReturnThreadEntity>();

    public DbSet<ReturnMessageEntity> ReturnMessages => Set<ReturnMessageEntity>();

    public DbSet<TemplateEntity> Templates => Set<TemplateEntity>();

    public DbSet<MailProviderEntity> MailProviders => Set<MailProviderEntity>();

    public DbSet<MailAccountEntity> MailAccounts => Set<MailAccountEntity>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        ConfigureMailDispatch(modelBuilder);
        ConfigureReturnThread(modelBuilder);
        ConfigureTemplate(modelBuilder);
        ConfigureProvider(modelBuilder);
    }

    private static void ConfigureMailDispatch(ModelBuilder modelBuilder)
    {
        var dispatch = modelBuilder.Entity<MailDispatchEntity>();
        dispatch.ToTable("mail_dispatches");
        dispatch.HasKey(entity => entity.Id);
        dispatch.HasIndex(entity => entity.TrackingId).IsUnique();
        dispatch.Property(entity => entity.TrackingId).HasMaxLength(64).IsRequired();
        dispatch.Property(entity => entity.TemplateKey).HasMaxLength(128).IsRequired();
        dispatch.Property(entity => entity.TemplateVersion).HasMaxLength(32).IsRequired();
        dispatch.Property(entity => entity.AccountId).HasMaxLength(64).IsRequired();
        dispatch.Property(entity => entity.AccountName).HasMaxLength(256).IsRequired();
        dispatch.Property(entity => entity.ProviderMessageId).HasMaxLength(256).IsRequired();
        dispatch.Property(entity => entity.ProviderThreadId).HasMaxLength(256);
        dispatch.Property(entity => entity.SentAt).IsRequired();
        dispatch.Property(entity => entity.LoggedAt).IsRequired();

        dispatch.HasMany(entity => entity.Recipients)
            .WithOne(entity => entity.Dispatch)
            .HasForeignKey(entity => entity.DispatchId)
            .OnDelete(DeleteBehavior.Cascade);

        var recipient = modelBuilder.Entity<MailRecipientEntity>();
        recipient.ToTable("mail_recipients");
        recipient.HasKey(entity => entity.Id);
        recipient.Property(entity => entity.Email).HasMaxLength(256).IsRequired();
        recipient.Property(entity => entity.Name).HasMaxLength(256);
        recipient.Property(entity => entity.Type)
            .HasConversion(new EnumToStringConverter<MailRecipientType>())
            .HasMaxLength(16)
            .IsRequired();
        recipient.HasIndex(entity => new { entity.DispatchId, entity.Type });
    }

    private static void ConfigureReturnThread(ModelBuilder modelBuilder)
    {
        var thread = modelBuilder.Entity<ReturnThreadEntity>();
        thread.ToTable("return_threads");
        thread.HasKey(entity => entity.Id);
        thread.HasIndex(entity => entity.TrackingKey).IsUnique();
        thread.Property(entity => entity.TrackingKey).HasMaxLength(64).IsRequired();
        thread.Property(entity => entity.HasValidTrackingId).IsRequired();
        thread.Property(entity => entity.SlaStatus)
            .HasConversion(new EnumToStringConverter<ReturnSlaStatus>())
            .HasMaxLength(32)
            .IsRequired();
        thread.Property(entity => entity.SlaStatusChangedAt).IsRequired();
        thread.Property(entity => entity.CreatedAt).IsRequired();
        thread.Property(entity => entity.UpdatedAt).IsRequired();
        thread.Property(entity => entity.LastFollowUpAt);

        thread.HasMany(entity => entity.Messages)
            .WithOne(entity => entity.Thread)
            .HasForeignKey(entity => entity.ThreadId)
            .OnDelete(DeleteBehavior.Cascade);

        var message = modelBuilder.Entity<ReturnMessageEntity>();
        message.ToTable("return_messages");
        message.HasKey(entity => entity.Id);
        message.HasIndex(entity => new { entity.ThreadId, entity.ProviderMessageId }).IsUnique();
        message.Property(entity => entity.ProviderMessageId).HasMaxLength(256).IsRequired();
        message.Property(entity => entity.AccountId).HasMaxLength(64).IsRequired();
        message.Property(entity => entity.ProviderType)
            .HasConversion(new EnumToStringConverter<MailProviderType>())
            .HasMaxLength(32)
            .IsRequired();
        message.Property(entity => entity.SenderAddress).HasMaxLength(256).IsRequired();
        message.Property(entity => entity.SenderName).HasMaxLength(256);
        message.Property(entity => entity.Subject).HasMaxLength(512).IsRequired();
        message.Property(entity => entity.BodyPreview).IsRequired();
        message.Property(entity => entity.Status)
            .HasConversion(new EnumToStringConverter<ReturnStatus>())
            .HasMaxLength(32)
            .IsRequired();
        message.Property(entity => entity.Score).HasPrecision(10, 4);
        message.Property(entity => entity.MatchedKeywordsJson).HasColumnName("matched_keywords_json").IsRequired();
        message.Property(entity => entity.ReasonsJson).HasColumnName("reasons_json").IsRequired();
        message.Property(entity => entity.RequiresManualReview).IsRequired();
        message.Property(entity => entity.ReceivedAt).IsRequired();
        message.Property(entity => entity.ConversationId).HasMaxLength(256);
        message.Property(entity => entity.MetadataJson).HasColumnName("metadata_json").IsRequired();
    }

    private static void ConfigureTemplate(ModelBuilder modelBuilder)
    {
        var template = modelBuilder.Entity<TemplateEntity>();
        template.ToTable("templates");
        template.HasKey(entity => entity.Id);
        template.HasIndex(entity => entity.Key).IsUnique();
        template.Property(entity => entity.Key).HasMaxLength(128).IsRequired();
        template.Property(entity => entity.DisplayName).HasMaxLength(256).IsRequired();
        template.Property(entity => entity.Version).HasMaxLength(32).IsRequired();
        template.Property(entity => entity.Subject).HasColumnName("subject_template").IsRequired();
        template.Property(entity => entity.Body).HasColumnName("body_html").IsRequired();
        template.Property(entity => entity.Description).HasMaxLength(512);
        template.Property(entity => entity.IsActive).IsRequired();
        template.Property(entity => entity.CreatedAt).IsRequired();
        template.Property(entity => entity.UpdatedAt).IsRequired();
    }

    private static void ConfigureProvider(ModelBuilder modelBuilder)
    {
        var provider = modelBuilder.Entity<MailProviderEntity>();
        provider.ToTable("mail_providers");
        provider.HasKey(entity => entity.Id);
        provider.HasIndex(entity => entity.Name).IsUnique();
        provider.Property(entity => entity.Name).HasMaxLength(64).IsRequired();
        provider.Property(entity => entity.DisplayName).HasMaxLength(256).IsRequired();
        provider.Property(entity => entity.Type)
            .HasConversion(new EnumToStringConverter<MailProviderType>())
            .HasMaxLength(32)
            .IsRequired();
        provider.Property(entity => entity.SettingsJson).HasColumnName("settings_json").IsRequired();
        provider.Property(entity => entity.IsActive).IsRequired();
        provider.Property(entity => entity.CreatedAt).IsRequired();
        provider.Property(entity => entity.UpdatedAt).IsRequired();

        provider.HasMany(entity => entity.Accounts)
            .WithOne(entity => entity.Provider)
            .HasForeignKey(entity => entity.ProviderId)
            .OnDelete(DeleteBehavior.Cascade);

        var account = modelBuilder.Entity<MailAccountEntity>();
        account.ToTable("mail_accounts");
        account.HasKey(entity => entity.Id);
        account.HasIndex(entity => entity.AccountId).IsUnique();
        account.Property(entity => entity.AccountId).HasMaxLength(64).IsRequired();
        account.Property(entity => entity.Address).HasMaxLength(256).IsRequired();
        account.Property(entity => entity.DisplayName).HasMaxLength(256);
        account.Property(entity => entity.MetadataJson).HasColumnName("metadata_json").IsRequired();
        account.Property(entity => entity.IsActive).IsRequired();
        account.Property(entity => entity.CreatedAt).IsRequired();
        account.Property(entity => entity.UpdatedAt).IsRequired();
    }
}
