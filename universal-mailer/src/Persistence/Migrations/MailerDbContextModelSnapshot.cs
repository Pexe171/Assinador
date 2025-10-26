using System;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using UniversalMailer.Core.Mail.Contracts;
using UniversalMailer.Core.Returns.Models;
using UniversalMailer.Persistence.Db;

#nullable disable

namespace UniversalMailer.Persistence.Migrations
{
    [DbContext(typeof(MailerDbContext))]
    partial class MailerDbContextModelSnapshot : ModelSnapshot
    {
        protected override void BuildModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder.HasAnnotation("ProductVersion", "8.0.4");

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.MailDispatchEntity", b =>
            {
                b.Property<Guid>("Id")
                    .ValueGeneratedOnAdd()
                    .HasColumnType("TEXT");

                b.Property<string>("AccountId")
                    .IsRequired()
                    .HasMaxLength(64)
                    .HasColumnType("TEXT");

                b.Property<string>("AccountName")
                    .IsRequired()
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("LoggedAt")
                    .HasColumnType("TEXT");

                b.Property<string>("ProviderMessageId")
                    .IsRequired()
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<string>("ProviderThreadId")
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("SentAt")
                    .HasColumnType("TEXT");

                b.Property<string>("TemplateKey")
                    .IsRequired()
                    .HasMaxLength(128)
                    .HasColumnType("TEXT");

                b.Property<string>("TemplateVersion")
                    .IsRequired()
                    .HasMaxLength(32)
                    .HasColumnType("TEXT");

                b.Property<string>("TrackingId")
                    .IsRequired()
                    .HasMaxLength(64)
                    .HasColumnType("TEXT");

                b.HasKey("Id");

                b.HasIndex("TrackingId")
                    .IsUnique();

                b.ToTable("mail_dispatches");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.MailRecipientEntity", b =>
            {
                b.Property<Guid>("Id")
                    .ValueGeneratedOnAdd()
                    .HasColumnType("TEXT");

                b.Property<Guid>("DispatchId")
                    .HasColumnType("TEXT");

                b.Property<string>("Email")
                    .IsRequired()
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<string>("Name")
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<string>("Type")
                    .IsRequired()
                    .HasMaxLength(16)
                    .HasColumnType("TEXT");

                b.HasKey("Id");

                b.HasIndex("DispatchId");

                b.HasIndex("DispatchId", "Type");

                b.ToTable("mail_recipients");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.MailProviderEntity", b =>
            {
                b.Property<Guid>("Id")
                    .ValueGeneratedOnAdd()
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("CreatedAt")
                    .HasColumnType("TEXT");

                b.Property<string>("DisplayName")
                    .IsRequired()
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<bool>("IsActive")
                    .HasColumnType("INTEGER");

                b.Property<string>("Name")
                    .IsRequired()
                    .HasMaxLength(64)
                    .HasColumnType("TEXT");

                b.Property<string>("settings_json")
                    .IsRequired()
                    .HasColumnType("TEXT");

                b.Property<string>("Type")
                    .IsRequired()
                    .HasMaxLength(32)
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("UpdatedAt")
                    .HasColumnType("TEXT");

                b.HasKey("Id");

                b.HasIndex("Name")
                    .IsUnique();

                b.ToTable("mail_providers");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.MailAccountEntity", b =>
            {
                b.Property<Guid>("Id")
                    .ValueGeneratedOnAdd()
                    .HasColumnType("TEXT");

                b.Property<string>("AccountId")
                    .IsRequired()
                    .HasMaxLength(64)
                    .HasColumnType("TEXT");

                b.Property<string>("Address")
                    .IsRequired()
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("CreatedAt")
                    .HasColumnType("TEXT");

                b.Property<string>("DisplayName")
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<bool>("IsActive")
                    .HasColumnType("INTEGER");

                b.Property<string>("metadata_json")
                    .IsRequired()
                    .HasColumnType("TEXT");

                b.Property<Guid>("ProviderId")
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("UpdatedAt")
                    .HasColumnType("TEXT");

                b.HasKey("Id");

                b.HasIndex("AccountId")
                    .IsUnique();

                b.HasIndex("ProviderId");

                b.ToTable("mail_accounts");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.ReturnThreadEntity", b =>
            {
                b.Property<Guid>("Id")
                    .ValueGeneratedOnAdd()
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("CreatedAt")
                    .HasColumnType("TEXT");

                b.Property<bool>("HasValidTrackingId")
                    .HasColumnType("INTEGER");

                b.Property<DateTimeOffset?>("LastFollowUpAt")
                    .HasColumnType("TEXT");

                b.Property<string>("SlaStatus")
                    .IsRequired()
                    .HasMaxLength(32)
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("SlaStatusChangedAt")
                    .HasColumnType("TEXT");

                b.Property<string>("TrackingKey")
                    .IsRequired()
                    .HasMaxLength(64)
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("UpdatedAt")
                    .HasColumnType("TEXT");

                b.HasKey("Id");

                b.HasIndex("TrackingKey")
                    .IsUnique();

                b.ToTable("return_threads");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.ReturnMessageEntity", b =>
            {
                b.Property<Guid>("Id")
                    .ValueGeneratedOnAdd()
                    .HasColumnType("TEXT");

                b.Property<string>("AccountId")
                    .IsRequired()
                    .HasMaxLength(64)
                    .HasColumnType("TEXT");

                b.Property<string>("BodyPreview")
                    .IsRequired()
                    .HasColumnType("TEXT");

                b.Property<string>("ConversationId")
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<string>("metadata_json")
                    .IsRequired()
                    .HasColumnType("TEXT");

                b.Property<string>("ProviderMessageId")
                    .IsRequired()
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<string>("ProviderType")
                    .IsRequired()
                    .HasMaxLength(32)
                    .HasColumnType("TEXT");

                b.Property<double>("Score")
                    .HasColumnType("REAL");

                b.Property<string>("SenderAddress")
                    .IsRequired()
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<string>("SenderName")
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("ReceivedAt")
                    .HasColumnType("TEXT");

                b.Property<bool>("RequiresManualReview")
                    .HasColumnType("INTEGER");

                b.Property<string>("reasons_json")
                    .IsRequired()
                    .HasColumnType("TEXT");

                b.Property<string>("matched_keywords_json")
                    .IsRequired()
                    .HasColumnType("TEXT");

                b.Property<string>("Status")
                    .IsRequired()
                    .HasMaxLength(32)
                    .HasColumnType("TEXT");

                b.Property<string>("Subject")
                    .IsRequired()
                    .HasMaxLength(512)
                    .HasColumnType("TEXT");

                b.Property<Guid>("ThreadId")
                    .HasColumnType("TEXT");

                b.HasKey("Id");

                b.HasIndex("ThreadId", "ProviderMessageId")
                    .IsUnique();

                b.ToTable("return_messages");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.TemplateEntity", b =>
            {
                b.Property<Guid>("Id")
                    .ValueGeneratedOnAdd()
                    .HasColumnType("TEXT");

                b.Property<string>("body_html")
                    .IsRequired()
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("CreatedAt")
                    .HasColumnType("TEXT");

                b.Property<string>("Description")
                    .HasMaxLength(512)
                    .HasColumnType("TEXT");

                b.Property<string>("DisplayName")
                    .IsRequired()
                    .HasMaxLength(256)
                    .HasColumnType("TEXT");

                b.Property<bool>("IsActive")
                    .HasColumnType("INTEGER");

                b.Property<string>("Key")
                    .IsRequired()
                    .HasMaxLength(128)
                    .HasColumnType("TEXT");

                b.Property<string>("subject_template")
                    .IsRequired()
                    .HasColumnType("TEXT");

                b.Property<DateTimeOffset>("UpdatedAt")
                    .HasColumnType("TEXT");

                b.Property<string>("Version")
                    .IsRequired()
                    .HasMaxLength(32)
                    .HasColumnType("TEXT");

                b.HasKey("Id");

                b.HasIndex("Key")
                    .IsUnique();

                b.ToTable("templates");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.MailRecipientEntity", b =>
            {
                b.HasOne("UniversalMailer.Persistence.Entities.MailDispatchEntity", "Dispatch")
                    .WithMany("Recipients")
                    .HasForeignKey("DispatchId")
                    .OnDelete(DeleteBehavior.Cascade)
                    .IsRequired();

                b.Navigation("Dispatch");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.MailAccountEntity", b =>
            {
                b.HasOne("UniversalMailer.Persistence.Entities.MailProviderEntity", "Provider")
                    .WithMany("Accounts")
                    .HasForeignKey("ProviderId")
                    .OnDelete(DeleteBehavior.Cascade)
                    .IsRequired();

                b.Navigation("Provider");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.ReturnMessageEntity", b =>
            {
                b.HasOne("UniversalMailer.Persistence.Entities.ReturnThreadEntity", "Thread")
                    .WithMany("Messages")
                    .HasForeignKey("ThreadId")
                    .OnDelete(DeleteBehavior.Cascade)
                    .IsRequired();

                b.Navigation("Thread");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.MailDispatchEntity", b =>
            {
                b.Navigation("Recipients");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.MailProviderEntity", b =>
            {
                b.Navigation("Accounts");
            });

            modelBuilder.Entity("UniversalMailer.Persistence.Entities.ReturnThreadEntity", b =>
            {
                b.Navigation("Messages");
            });
#pragma warning restore 612, 618
        }
    }
}
