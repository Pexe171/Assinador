#include "data/database_manager.h"

#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>
#include <QSqlError>
#include <QSqlQuery>
#include <QStringList>
#include <QTextStream>

namespace assinador::data {

namespace {
constexpr auto kDriver = "QSQLITE";
constexpr auto kDatabaseFilename = "assinador.sqlite";
}

DatabaseManager &DatabaseManager::instance()
{
    static DatabaseManager instancia;
    return instancia;
}

DatabaseManager::DatabaseManager()
{
    garantirDiretorios();

    const auto basePath = QCoreApplication::applicationDirPath();
    QDir dataDir(basePath + "/data");
    m_caminhoBanco = dataDir.filePath(kDatabaseFilename);

    if (QSqlDatabase::contains("assinador")) {
        m_banco = QSqlDatabase::database("assinador");
    } else {
        m_banco = QSqlDatabase::addDatabase(kDriver, "assinador");
    }

    if (m_banco.databaseName().isEmpty()) {
        m_banco.setDatabaseName(m_caminhoBanco);
    } else {
        m_caminhoBanco = m_banco.databaseName();
    }
}

bool DatabaseManager::abrirConexao()
{
    if (m_banco.isOpen()) {
        return true;
    }

    if (!m_banco.open()) {
        QTextStream(stderr) << "Falha ao abrir banco SQLite: " << m_banco.lastError().text() << '\n';
        return false;
    }

    return aplicarMigracoesIniciais();
}

void DatabaseManager::fecharConexao()
{
    if (m_banco.isOpen()) {
        m_banco.close();
    }
}

QString DatabaseManager::caminhoBanco() const
{
    return m_caminhoBanco;
}

QSqlDatabase DatabaseManager::conexao() const
{
    return m_banco;
}

bool DatabaseManager::aplicarMigracoesIniciais()
{
    QSqlQuery query(m_banco);

    const QStringList comandos {
        QStringLiteral(
            "CREATE TABLE IF NOT EXISTS cadastros ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "codigo TEXT NOT NULL UNIQUE,"
            "nome TEXT NOT NULL,"
            "email TEXT,"
            "renda REAL DEFAULT 0,"
            "status TEXT DEFAULT 'Pendente',"
            "observacoes TEXT,"
            "criado_em DATETIME DEFAULT CURRENT_TIMESTAMP"
            ");"
        ),
        QStringLiteral(
            "CREATE TABLE IF NOT EXISTS envios_log ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "cadastro_codigo TEXT NOT NULL,"
            "modelo TEXT NOT NULL,"
            "status_envio TEXT NOT NULL,"
            "mensagem TEXT,"
            "criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,"
            "FOREIGN KEY(cadastro_codigo) REFERENCES cadastros(codigo) ON DELETE CASCADE"
            ");"
        ),
        QStringLiteral(
            "CREATE INDEX IF NOT EXISTS idx_cadastros_codigo ON cadastros(codigo);"
        ),
        QStringLiteral(
            "CREATE INDEX IF NOT EXISTS idx_envios_log_cadastro_codigo ON envios_log(cadastro_codigo);"
        )
    };

    for (const auto &ddl : comandos) {
        if (!query.exec(ddl)) {
            QTextStream(stderr) << "Erro ao aplicar migração inicial: " << query.lastError().text() << '\n';
            return false;
        }
    }

    return true;
}

void DatabaseManager::garantirDiretorios()
{
    const auto basePath = QCoreApplication::applicationDirPath();
    QDir baseDir(basePath);

    if (!baseDir.exists("data")) {
        baseDir.mkpath("data");
    }

    if (!baseDir.exists("resources/oft")) {
        baseDir.mkpath("resources/oft");
    }
}

} // namespace assinador::data
