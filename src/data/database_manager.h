#pragma once

#include <QSqlDatabase>

namespace assinador::data {

/**
 * @brief Responsável por gerenciar a conexão SQLite e rodar migrações iniciais.
 */
class DatabaseManager {
public:
    static DatabaseManager &instance();

    bool abrirConexao();
    void fecharConexao();
    [[nodiscard]] QString caminhoBanco() const;

private:
    DatabaseManager();
    bool aplicarMigracoesIniciais();
    void garantirDiretorios();

    QSqlDatabase m_banco;
    QString m_caminhoBanco;
};

} // namespace assinador::data
