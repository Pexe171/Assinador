#include <QtTest>

#include <QSqlDatabase>
#include <QSqlError>
#include <QSqlQuery>
#include <QVariant>

#include "data/database_manager.h"

using assinador::data::DatabaseManager;

class DatabaseManagerTest final : public QObject {
    Q_OBJECT

private slots:
    void initTestCase();
    void testTabelaCadastrosEhCriada();
    void testInserirEConsultarCadastro();
    void cleanupTestCase();

private:
    QSqlDatabase m_bancoTeste;
};

void DatabaseManagerTest::initTestCase()
{
    if (QSqlDatabase::contains("assinador")) {
        QSqlDatabase::removeDatabase("assinador");
    }

    m_bancoTeste = QSqlDatabase::addDatabase("QSQLITE", "assinador");
    m_bancoTeste.setDatabaseName(":memory:");

    QVERIFY2(DatabaseManager::instance().abrirConexao(), "Falha ao abrir conexão com o banco em memória");
    QVERIFY2(m_bancoTeste.isOpen(), "Banco em memória deveria estar aberto após abrirConexao()");
}

void DatabaseManagerTest::testTabelaCadastrosEhCriada()
{
    QSqlQuery query(m_bancoTeste);
    QVERIFY2(query.exec("SELECT name FROM sqlite_master WHERE type='table' AND name='cadastros';"),
             qPrintable(query.lastError().text()));
    QVERIFY2(query.next(), "Tabela 'cadastros' deveria existir após migração inicial");
    QCOMPARE(query.value(0).toString(), QStringLiteral("cadastros"));
    QVERIFY(!query.next());
}

void DatabaseManagerTest::testInserirEConsultarCadastro()
{
    QSqlQuery insert(m_bancoTeste);
    QVERIFY2(insert.prepare("INSERT INTO cadastros (nome, email) VALUES (?, ?);"),
             qPrintable(insert.lastError().text()));
    insert.addBindValue(QStringLiteral("Fulano de Tal"));
    insert.addBindValue(QStringLiteral("fulano@example.com"));
    QVERIFY2(insert.exec(), qPrintable(insert.lastError().text()));

    QSqlQuery select(m_bancoTeste);
    QVERIFY2(select.prepare("SELECT nome, email FROM cadastros WHERE nome = ?;"),
             qPrintable(select.lastError().text()));
    select.addBindValue(QStringLiteral("Fulano de Tal"));
    QVERIFY2(select.exec(), qPrintable(select.lastError().text()));
    QVERIFY2(select.next(), "Registro recém inserido deveria ser retornado");
    QCOMPARE(select.value(0).toString(), QStringLiteral("Fulano de Tal"));
    QCOMPARE(select.value(1).toString(), QStringLiteral("fulano@example.com"));
    QVERIFY(!select.next());
}

void DatabaseManagerTest::cleanupTestCase()
{
    DatabaseManager::instance().fecharConexao();
    m_bancoTeste = QSqlDatabase();
    QSqlDatabase::removeDatabase("assinador");
}

QTEST_APPLESS_MAIN(DatabaseManagerTest)

#include "test_database_manager.moc"
