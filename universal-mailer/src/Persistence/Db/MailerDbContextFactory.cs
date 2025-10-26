using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace UniversalMailer.Persistence.Db;

public sealed class MailerDbContextFactory : IDesignTimeDbContextFactory<MailerDbContext>
{
    public MailerDbContext CreateDbContext(string[] args)
    {
        var optionsBuilder = new DbContextOptionsBuilder<MailerDbContext>();
        const string connectionString = "Data Source=../db/mailer.db";
        optionsBuilder.UseSqlite(connectionString);
        return new MailerDbContext(optionsBuilder.Options);
    }
}
