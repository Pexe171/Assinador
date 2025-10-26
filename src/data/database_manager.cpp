#include "data/database_manager.h"

#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>
#include <QSqlError>
#include <QSqlQuery>
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

    m_banco.setDatabaseName(m_caminhoBanco);
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

bool DatabaseManager::aplicarMigracoesIniciais()
{
    QSqlQuery query(m_banco);
    const auto ddl = QStringLiteral(
        "CREATE TABLE IF NOT EXISTS cadastros ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "nome TEXT NOT NULL,"
        "email TEXT,"
        "criado_em DATETIME DEFAULT CURRENT_TIMESTAMP"
        ");"
    );

    if (!query.exec(ddl)) {
        QTextStream(stderr) << "Erro ao aplicar migração inicial: " << query.lastError().text() << '\n';
        return false;
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
