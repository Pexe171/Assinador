#pragma once

#include "data/cadastro_repository.h"
#include "integration/outlook_automation.h"

#include <QWidget>

#include <optional>

class QComboBox;
class QDoubleSpinBox;
class QLabel;
class QLineEdit;
class QPushButton;
class QTextEdit;

namespace assinador::ui {

class CadastroForm : public QWidget {
    Q_OBJECT

public:
    explicit CadastroForm(QWidget *parent = nullptr);

signals:
    void cadastroCriado(const assinador::data::Cadastro &cadastro);

private slots:
    void salvarCadastro();
    void enviarEmail();
    void limparFormulario();

private:
    void montarLayout();
    void prepararSinais();
    void atualizarResumo(const QString &mensagem, bool sucesso);

    data::CadastroRepository m_repositorio;
    integration::OutlookAutomation m_outlook;
    std::optional<data::Cadastro> m_cadastroAtual;

    QLineEdit *m_nomeEdit {nullptr};
    QLineEdit *m_emailEdit {nullptr};
    QDoubleSpinBox *m_rendaSpin {nullptr};
    QComboBox *m_statusCombo {nullptr};
    QTextEdit *m_observacoesEdit {nullptr};
    QLineEdit *m_modeloEdit {nullptr};
    QLabel *m_codigoLabel {nullptr};
    QLabel *m_resumoLabel {nullptr};
    QPushButton *m_salvarButton {nullptr};
    QPushButton *m_enviarButton {nullptr};
    QPushButton *m_limparButton {nullptr};
};

} // namespace assinador::ui
