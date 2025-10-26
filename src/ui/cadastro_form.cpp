#include "ui/cadastro_form.h"

#include <QComboBox>
#include <QDateTime>
#include <QDoubleSpinBox>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QMap>
#include <QMessageBox>
#include <QPushButton>
#include <QTextEdit>
#include <QVBoxLayout>

using assinador::data::Cadastro;
using assinador::ui::CadastroForm;

CadastroForm::CadastroForm(QWidget *parent)
    : QWidget(parent)
{
    montarLayout();
    prepararSinais();
    atualizarResumo(tr("Preencha os campos e clique em salvar para gerar um código."), true);
}

void CadastroForm::montarLayout()
{
    auto *layoutPrincipal = new QVBoxLayout(this);

    auto *formLayout = new QFormLayout();
    m_nomeEdit = new QLineEdit(this);
    m_nomeEdit->setPlaceholderText(tr("Ex.: Maria da Silva"));
    formLayout->addRow(tr("Nome completo"), m_nomeEdit);

    m_emailEdit = new QLineEdit(this);
    m_emailEdit->setPlaceholderText(tr("exemplo@empresa.com"));
    formLayout->addRow(tr("E-mail"), m_emailEdit);

    m_rendaSpin = new QDoubleSpinBox(this);
    m_rendaSpin->setPrefix("R$ ");
    m_rendaSpin->setMaximum(1'000'000'000.0);
    m_rendaSpin->setDecimals(2);
    formLayout->addRow(tr("Renda mensal"), m_rendaSpin);

    m_statusCombo = new QComboBox(this);
    m_statusCombo->addItems({tr("Pendente"), tr("Aprovado"), tr("Rejeitado")});
    formLayout->addRow(tr("Status"), m_statusCombo);

    m_observacoesEdit = new QTextEdit(this);
    m_observacoesEdit->setPlaceholderText(tr("Inclua orientações, acordos ou observações relevantes."));
    m_observacoesEdit->setFixedHeight(80);
    formLayout->addRow(tr("Observações"), m_observacoesEdit);

    m_modeloEdit = new QLineEdit(this);
    m_modeloEdit->setPlaceholderText(tr("cadastro_padrao.oft"));
    formLayout->addRow(tr("Modelo de e-mail"), m_modeloEdit);

    m_codigoLabel = new QLabel(tr("Código ainda não gerado."), this);
    m_codigoLabel->setObjectName("codigoLabel");

    layoutPrincipal->addLayout(formLayout);
    layoutPrincipal->addWidget(m_codigoLabel);

    auto *botoesLayout = new QHBoxLayout();
    m_salvarButton = new QPushButton(tr("Salvar cadastro"), this);
    m_enviarButton = new QPushButton(tr("Enviar e-mail"), this);
    m_limparButton = new QPushButton(tr("Limpar"), this);
    m_enviarButton->setEnabled(false);

    botoesLayout->addWidget(m_salvarButton);
    botoesLayout->addWidget(m_enviarButton);
    botoesLayout->addWidget(m_limparButton);

    layoutPrincipal->addLayout(botoesLayout);

    m_resumoLabel = new QLabel(this);
    m_resumoLabel->setWordWrap(true);
    layoutPrincipal->addWidget(m_resumoLabel);
    layoutPrincipal->addStretch();
}

void CadastroForm::prepararSinais()
{
    connect(m_salvarButton, &QPushButton::clicked, this, &CadastroForm::salvarCadastro);
    connect(m_enviarButton, &QPushButton::clicked, this, &CadastroForm::enviarEmail);
    connect(m_limparButton, &QPushButton::clicked, this, &CadastroForm::limparFormulario);
}

void CadastroForm::salvarCadastro()
{
    const auto nome = m_nomeEdit->text().trimmed();
    if (nome.isEmpty()) {
        QMessageBox::warning(this, tr("Informação incompleta"), tr("Informe o nome completo."));
        return;
    }

    const auto email = m_emailEdit->text().trimmed();
    const auto renda = m_rendaSpin->value();
    const auto status = m_statusCombo->currentText();
    const auto observacoes = m_observacoesEdit->toPlainText().trimmed();

    const auto cadastro = m_repositorio.criarCadastro(nome, email, renda, status, observacoes);
    if (!cadastro.has_value()) {
        atualizarResumo(tr("Não foi possível salvar. Verifique o log no terminal."), false);
        return;
    }

    m_cadastroAtual = cadastro;
    m_enviarButton->setEnabled(true);
    m_codigoLabel->setText(tr("Código gerado: %1").arg(cadastro->codigo));
    atualizarResumo(tr("Cadastro salvo com sucesso."), true);
    emit cadastroCriado(cadastro.value());
}

void CadastroForm::enviarEmail()
{
    if (!m_cadastroAtual.has_value()) {
        QMessageBox::information(this, tr("Cadastro necessário"), tr("Salve o cadastro antes de enviar o e-mail."));
        return;
    }

    const auto modelo = m_modeloEdit->text().trimmed().isEmpty() ? QStringLiteral("cadastro_padrao.oft")
                                                                 : m_modeloEdit->text().trimmed();

    const auto cadastro = m_cadastroAtual.value();
    QMap<QString, QString> placeholders {
        {QStringLiteral("{{CODIGO}}"), cadastro.codigo},
        {QStringLiteral("{{NOME}}"), cadastro.nome},
        {QStringLiteral("{{EMAIL}}"), cadastro.email},
        {QStringLiteral("{{RENDA}}"), QString::number(cadastro.renda, 'f', 2)},
        {QStringLiteral("{{STATUS}}"), cadastro.status},
        {QStringLiteral("{{DATA_CADASTRO}}"), cadastro.criadoEm.toString(Qt::ISODate)}
    };

    const auto resultado = m_outlook.enviarModelo(modelo, placeholders);
    const auto statusEnvio = resultado ? tr("Sucesso") : tr("Falha");
    const auto mensagem = resultado
        ? tr("Modelo %1 enviado para conferência no Outlook.").arg(modelo)
        : tr("Não foi possível abrir o modelo %1. Veja mensagens no terminal.").arg(modelo);

    m_repositorio.registrarEnvioEmail(cadastro.codigo, modelo, statusEnvio, mensagem);

    if (resultado) {
        atualizarResumo(mensagem, true);
        QMessageBox::information(this, tr("E-mail preparado"), mensagem);
    } else {
        atualizarResumo(mensagem, false);
        QMessageBox::warning(this, tr("Envio não concluído"), mensagem);
    }
}

void CadastroForm::limparFormulario()
{
    m_nomeEdit->clear();
    m_emailEdit->clear();
    m_rendaSpin->setValue(0.0);
    m_statusCombo->setCurrentIndex(0);
    m_observacoesEdit->clear();
    m_modeloEdit->clear();
    m_codigoLabel->setText(tr("Código ainda não gerado."));
    m_cadastroAtual.reset();
    m_enviarButton->setEnabled(false);
    atualizarResumo(tr("Formulário limpo."), true);
}

void CadastroForm::atualizarResumo(const QString &mensagem, bool sucesso)
{
    const auto cor = sucesso ? QStringLiteral("#2e7d32") : QStringLiteral("#c62828");
    m_resumoLabel->setText(
        tr("<b>Status:</b> <span style=\"color:%1\">%2</span>").arg(cor, mensagem)
    );
}
