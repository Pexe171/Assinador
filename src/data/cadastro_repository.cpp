#include "data/cadastro_repository.h"

#include <QSqlError>
#include <QSqlQuery>
#include <QSqlRecord>
#include <QTextStream>

namespace assinador::data {

CadastroRepository::CadastroRepository()
    : m_banco(DatabaseManager::instance().conexao())
{
}

std::optional<Cadastro> CadastroRepository::criarCadastro(const QString &nome,
                                                          const QString &email,
                                                          double renda,
                                                          const QString &status,
                                                          const QString &observacoes) const
{
    if (!m_banco.isValid()) {
        QTextStream(stderr) << "Conexão com o banco inválida."
                            << '\n';
        return std::nullopt;
    }

    const auto codigo = gerarProximoCodigo();

    if (!m_banco.transaction()) {
        QTextStream(stderr) << "Não foi possível iniciar transação: "
                            << m_banco.lastError().text() << '\n';
        return std::nullopt;
    }

    QSqlQuery insert(m_banco);
    insert.prepare(
        "INSERT INTO cadastros (codigo, nome, email, renda, status, observacoes) "
        "VALUES (?, ?, ?, ?, ?, ?)"
    );
    insert.addBindValue(codigo);
    insert.addBindValue(nome);
    insert.addBindValue(email);
    insert.addBindValue(renda);
    insert.addBindValue(status);
    insert.addBindValue(observacoes);

    if (!insert.exec()) {
        QTextStream(stderr) << "Erro ao salvar cadastro: " << insert.lastError().text() << '\n';
        m_banco.rollback();
        return std::nullopt;
    }

    const auto id = insert.lastInsertId().toInt();
    if (!m_banco.commit()) {
        QTextStream(stderr) << "Falha ao confirmar cadastro: " << m_banco.lastError().text() << '\n';
        m_banco.rollback();
        return std::nullopt;
    }

    QSqlQuery select(m_banco);
    select.prepare(
        "SELECT id, codigo, nome, email, renda, status, observacoes, criado_em "
        "FROM cadastros WHERE id = ?"
    );
    select.addBindValue(id);

    if (!select.exec() || !select.next()) {
        QTextStream(stderr) << "Não foi possível recuperar cadastro recém-criado."
                            << '\n';
        return std::nullopt;
    }

    Cadastro cadastro;
    cadastro.id = select.value("id").toInt();
    cadastro.codigo = select.value("codigo").toString();
    cadastro.nome = select.value("nome").toString();
    cadastro.email = select.value("email").toString();
    cadastro.renda = select.value("renda").toDouble();
    cadastro.status = select.value("status").toString();
    cadastro.observacoes = select.value("observacoes").toString();
    cadastro.criadoEm = select.value("criado_em").toDateTime();

    return cadastro;
}

QVector<Cadastro> CadastroRepository::listarCadastros(const QString &filtroTexto) const
{
    QVector<Cadastro> cadastros;
    QSqlQuery query(m_banco);

    if (filtroTexto.trimmed().isEmpty()) {
        query.prepare(
            "SELECT id, codigo, nome, email, renda, status, observacoes, criado_em "
            "FROM cadastros ORDER BY criado_em DESC"
        );
    } else {
        const auto filtro = '%' + filtroTexto.trimmed() + '%';
        query.prepare(
            "SELECT id, codigo, nome, email, renda, status, observacoes, criado_em "
            "FROM cadastros "
            "WHERE codigo LIKE ? OR nome LIKE ? OR email LIKE ? "
            "ORDER BY criado_em DESC"
        );
        query.addBindValue(filtro);
        query.addBindValue(filtro);
        query.addBindValue(filtro);
    }

    if (!query.exec()) {
        QTextStream(stderr) << "Erro ao consultar cadastros: " << query.lastError().text() << '\n';
        return cadastros;
    }

    while (query.next()) {
        Cadastro cadastro;
        cadastro.id = query.value("id").toInt();
        cadastro.codigo = query.value("codigo").toString();
        cadastro.nome = query.value("nome").toString();
        cadastro.email = query.value("email").toString();
        cadastro.renda = query.value("renda").toDouble();
        cadastro.status = query.value("status").toString();
        cadastro.observacoes = query.value("observacoes").toString();
        cadastro.criadoEm = query.value("criado_em").toDateTime();
        cadastros.append(cadastro);
    }

    return cadastros;
}

void CadastroRepository::registrarEnvioEmail(const QString &codigoCadastro,
                                             const QString &modelo,
                                             const QString &statusEnvio,
                                             const QString &mensagem) const
{
    QSqlQuery query(m_banco);
    query.prepare(
        "INSERT INTO envios_log (cadastro_codigo, modelo, status_envio, mensagem) "
        "VALUES (?, ?, ?, ?)"
    );
    query.addBindValue(codigoCadastro);
    query.addBindValue(modelo);
    query.addBindValue(statusEnvio);
    query.addBindValue(mensagem);

    if (!query.exec()) {
        QTextStream(stderr) << "Falha ao registrar log de envio: " << query.lastError().text() << '\n';
    }
}

QVector<LogEnvio> CadastroRepository::listarLogsPorCadastro(const QString &codigoCadastro) const
{
    QVector<LogEnvio> logs;
    QSqlQuery query(m_banco);
    query.prepare(
        "SELECT id, cadastro_codigo, modelo, status_envio, mensagem, criado_em "
        "FROM envios_log WHERE cadastro_codigo = ? "
        "ORDER BY criado_em DESC"
    );
    query.addBindValue(codigoCadastro);

    if (!query.exec()) {
        QTextStream(stderr) << "Erro ao buscar logs: " << query.lastError().text() << '\n';
        return logs;
    }

    while (query.next()) {
        LogEnvio log;
        log.id = query.value("id").toInt();
        log.codigoCadastro = query.value("cadastro_codigo").toString();
        log.modelo = query.value("modelo").toString();
        log.statusEnvio = query.value("status_envio").toString();
        log.mensagem = query.value("mensagem").toString();
        log.criadoEm = query.value("criado_em").toDateTime();
        logs.append(log);
    }

    return logs;
}

QString CadastroRepository::gerarProximoCodigo() const
{
    QSqlQuery query(m_banco);
    query.prepare(
        "SELECT codigo FROM cadastros ORDER BY id DESC LIMIT 1"
    );

    if (!query.exec() || !query.next()) {
        return QStringLiteral("AC-0001");
    }

    const auto ultimoCodigo = query.value(0).toString();
    const auto sequencial = extrairSequencial(ultimoCodigo) + 1;
    return QStringLiteral("AC-%1").arg(sequencial, 4, 10, QLatin1Char('0'));
}

int CadastroRepository::extrairSequencial(const QString &codigo)
{
    const auto partes = codigo.split('-');
    if (partes.size() != 2) {
        return 0;
    }

    bool ok = false;
    const auto numero = partes.at(1).toInt(&ok);
    return ok ? numero : 0;
}

} // namespace assinador::data
