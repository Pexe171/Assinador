#pragma once

#include "data/cadastro_repository.h"

#include <QString>
#include <QWidget>

class QLineEdit;
class QTableWidget;
class QPushButton;

namespace assinador::ui {

class ConsultaWidget : public QWidget {
    Q_OBJECT

public:
    explicit ConsultaWidget(QWidget *parent = nullptr);

public slots:
    void recarregarCadastros();
    void aplicarFiltro(const QString &texto);

private slots:
    void aoSelecionarCadastro(int linha, int coluna);

private:
    void montarLayout();
    void atualizarTabelaCadastros(const QVector<assinador::data::Cadastro> &cadastros);
    void atualizarTabelaLogs(const QVector<assinador::data::LogEnvio> &logs);

    data::CadastroRepository m_repositorio;

    QLineEdit *m_pesquisaEdit {nullptr};
    QPushButton *m_recarregarButton {nullptr};
    QTableWidget *m_tabelaCadastros {nullptr};
    QTableWidget *m_tabelaLogs {nullptr};
    QString m_filtroAtual;
};

} // namespace assinador::ui
