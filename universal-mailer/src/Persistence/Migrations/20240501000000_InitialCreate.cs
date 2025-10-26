using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace UniversalMailer.Persistence.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "mail_dispatches",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    TrackingId = table.Column<string>(type: "TEXT", maxLength: 64, nullable: false),
                    TemplateKey = table.Column<string>(type: "TEXT", maxLength: 128, nullable: false),
                    TemplateVersion = table.Column<string>(type: "TEXT", maxLength: 32, nullable: false),
                    AccountId = table.Column<string>(type: "TEXT", maxLength: 64, nullable: false),
                    AccountName = table.Column<string>(type: "TEXT", maxLength: 256, nullable: false),
                    ProviderMessageId = table.Column<string>(type: "TEXT", maxLength: 256, nullable: false),
                    ProviderThreadId = table.Column<string>(type: "TEXT", maxLength: 256, nullable: true),
                    SentAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false),
                    LoggedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mail_dispatches", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "mail_providers",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    Name = table.Column<string>(type: "TEXT", maxLength: 64, nullable: false),
                    DisplayName = table.Column<string>(type: "TEXT", maxLength: 256, nullable: false),
                    Type = table.Column<string>(type: "TEXT", maxLength: 32, nullable: false),
                    settings_json = table.Column<string>(type: "TEXT", nullable: false),
                    IsActive = table.Column<bool>(type: "INTEGER", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false),
                    UpdatedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mail_providers", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "return_threads",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    TrackingKey = table.Column<string>(type: "TEXT", maxLength: 64, nullable: false),
                    HasValidTrackingId = table.Column<bool>(type: "INTEGER", nullable: false),
                    SlaStatus = table.Column<string>(type: "TEXT", maxLength: 32, nullable: false),
                    SlaStatusChangedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false),
                    UpdatedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false),
                    LastFollowUpAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_return_threads", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "templates",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    Key = table.Column<string>(type: "TEXT", maxLength: 128, nullable: false),
                    DisplayName = table.Column<string>(type: "TEXT", maxLength: 256, nullable: false),
                    Version = table.Column<string>(type: "TEXT", maxLength: 32, nullable: false),
                    subject_template = table.Column<string>(type: "TEXT", nullable: false),
                    body_html = table.Column<string>(type: "TEXT", nullable: false),
                    Description = table.Column<string>(type: "TEXT", maxLength: 512, nullable: true),
                    IsActive = table.Column<bool>(type: "INTEGER", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false),
                    UpdatedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_templates", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "mail_recipients",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    DispatchId = table.Column<Guid>(type: "TEXT", nullable: false),
                    Type = table.Column<string>(type: "TEXT", maxLength: 16, nullable: false),
                    Email = table.Column<string>(type: "TEXT", maxLength: 256, nullable: false),
                    Name = table.Column<string>(type: "TEXT", maxLength: 256, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mail_recipients", x => x.Id);
                    table.ForeignKey(
                        name: "FK_mail_recipients_mail_dispatches_DispatchId",
                        column: x => x.DispatchId,
                        principalTable: "mail_dispatches",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "mail_accounts",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    AccountId = table.Column<string>(type: "TEXT", maxLength: 64, nullable: false),
                    Address = table.Column<string>(type: "TEXT", maxLength: 256, nullable: false),
                    DisplayName = table.Column<string>(type: "TEXT", maxLength: 256, nullable: true),
                    metadata_json = table.Column<string>(type: "TEXT", nullable: false),
                    IsActive = table.Column<bool>(type: "INTEGER", nullable: false),
                    ProviderId = table.Column<Guid>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false),
                    UpdatedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mail_accounts", x => x.Id);
                    table.ForeignKey(
                        name: "FK_mail_accounts_mail_providers_ProviderId",
                        column: x => x.ProviderId,
                        principalTable: "mail_providers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "return_messages",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "TEXT", nullable: false),
                    ThreadId = table.Column<Guid>(type: "TEXT", nullable: false),
                    ProviderMessageId = table.Column<string>(type: "TEXT", maxLength: 256, nullable: false),
                    AccountId = table.Column<string>(type: "TEXT", maxLength: 64, nullable: false),
                    ProviderType = table.Column<string>(type: "TEXT", maxLength: 32, nullable: false),
                    SenderAddress = table.Column<string>(type: "TEXT", maxLength: 256, nullable: false),
                    SenderName = table.Column<string>(type: "TEXT", maxLength: 256, nullable: true),
                    Subject = table.Column<string>(type: "TEXT", maxLength: 512, nullable: false),
                    BodyPreview = table.Column<string>(type: "TEXT", nullable: false),
                    Status = table.Column<string>(type: "TEXT", maxLength: 32, nullable: false),
                    Score = table.Column<double>(type: "REAL", nullable: false),
                    matched_keywords_json = table.Column<string>(type: "TEXT", nullable: false),
                    reasons_json = table.Column<string>(type: "TEXT", nullable: false),
                    RequiresManualReview = table.Column<bool>(type: "INTEGER", nullable: false),
                    ReceivedAt = table.Column<DateTimeOffset>(type: "TEXT", nullable: false),
                    ConversationId = table.Column<string>(type: "TEXT", maxLength: 256, nullable: true),
                    metadata_json = table.Column<string>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_return_messages", x => x.Id);
                    table.ForeignKey(
                        name: "FK_return_messages_return_threads_ThreadId",
                        column: x => x.ThreadId,
                        principalTable: "return_threads",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_mail_accounts_AccountId",
                table: "mail_accounts",
                column: "AccountId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_mail_accounts_ProviderId",
                table: "mail_accounts",
                column: "ProviderId");

            migrationBuilder.CreateIndex(
                name: "IX_mail_dispatches_TrackingId",
                table: "mail_dispatches",
                column: "TrackingId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_mail_providers_Name",
                table: "mail_providers",
                column: "Name",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_mail_recipients_DispatchId",
                table: "mail_recipients",
                column: "DispatchId");

            migrationBuilder.CreateIndex(
                name: "IX_mail_recipients_DispatchId_Type",
                table: "mail_recipients",
                columns: new[] { "DispatchId", "Type" });

            migrationBuilder.CreateIndex(
                name: "IX_return_messages_ThreadId_ProviderMessageId",
                table: "return_messages",
                columns: new[] { "ThreadId", "ProviderMessageId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_return_threads_TrackingKey",
                table: "return_threads",
                column: "TrackingKey",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_templates_Key",
                table: "templates",
                column: "Key",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "mail_accounts");

            migrationBuilder.DropTable(
                name: "mail_recipients");

            migrationBuilder.DropTable(
                name: "return_messages");

            migrationBuilder.DropTable(
                name: "templates");

            migrationBuilder.DropTable(
                name: "mail_providers");

            migrationBuilder.DropTable(
                name: "mail_dispatches");

            migrationBuilder.DropTable(
                name: "return_threads");
        }
    }
}
