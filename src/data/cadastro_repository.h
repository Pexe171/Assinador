#pragma once

#include "data/database_manager.h"

#include <QDateTime>
#include <QString>
#include <QVector>

#include <optional>

namespace assinador::data {

struct Cadastro {
    int id {0};
    QString codigo;
    QString nome;
    QString email;
    double renda {0.0};
    QString status;
    QString observacoes;
    QDateTime criadoEm;
};

struct LogEnvio {
    int id {0};
    QString codigoCadastro;
    QString modelo;
    QString statusEnvio;
    QString mensagem;
    QDateTime criadoEm;
};

class CadastroRepository {
public:
    CadastroRepository();

    std::optional<Cadastro> criarCadastro(const QString &nome,
                                          const QString &email,
                                          double renda,
                                          const QString &status,
                                          const QString &observacoes) const;

    QVector<Cadastro> listarCadastros(const QString &filtroTexto = QString()) const;

    void registrarEnvioEmail(const QString &codigoCadastro,
                             const QString &modelo,
                             const QString &statusEnvio,
                             const QString &mensagem) const;

    QVector<LogEnvio> listarLogsPorCadastro(const QString &codigoCadastro) const;

private:
    QString gerarProximoCodigo() const;
    static int extrairSequencial(const QString &codigo);

    QSqlDatabase m_banco;
};

} // namespace assinador::data
