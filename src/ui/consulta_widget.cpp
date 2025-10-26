#include "ui/consulta_widget.h"

#include <QAbstractItemView>
#include <QHeaderView>
#include <QHBoxLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QTableWidget>
#include <QTableWidgetItem>
#include <QVBoxLayout>

using assinador::data::Cadastro;
using assinador::data::LogEnvio;
using assinador::ui::ConsultaWidget;

ConsultaWidget::ConsultaWidget(QWidget *parent)
    : QWidget(parent)
{
    montarLayout();
    recarregarCadastros();
}

void ConsultaWidget::montarLayout()
{
    auto *layoutPrincipal = new QVBoxLayout(this);

    auto *filtroLayout = new QHBoxLayout();
    m_pesquisaEdit = new QLineEdit(this);
    m_pesquisaEdit->setPlaceholderText(tr("Busque por código, nome ou e-mail"));
    m_recarregarButton = new QPushButton(tr("Atualizar"), this);

    filtroLayout->addWidget(m_pesquisaEdit);
    filtroLayout->addWidget(m_recarregarButton);

    layoutPrincipal->addLayout(filtroLayout);

    m_tabelaCadastros = new QTableWidget(this);
    m_tabelaCadastros->setColumnCount(6);
    m_tabelaCadastros->setHorizontalHeaderLabels({
        tr("Código"), tr("Nome"), tr("E-mail"), tr("Renda"), tr("Status"), tr("Criado em")
    });
    m_tabelaCadastros->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_tabelaCadastros->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_tabelaCadastros->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_tabelaCadastros->setAlternatingRowColors(true);

    m_tabelaLogs = new QTableWidget(this);
    m_tabelaLogs->setColumnCount(4);
    m_tabelaLogs->setHorizontalHeaderLabels({
        tr("Data/Hora"), tr("Modelo"), tr("Status"), tr("Mensagem")
    });
    m_tabelaLogs->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    m_tabelaLogs->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_tabelaLogs->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_tabelaLogs->setAlternatingRowColors(true);

    layoutPrincipal->addWidget(m_tabelaCadastros, 3);
    layoutPrincipal->addWidget(m_tabelaLogs, 2);

    connect(m_recarregarButton, &QPushButton::clicked, this, &ConsultaWidget::recarregarCadastros);
    connect(m_pesquisaEdit, &QLineEdit::textChanged, this, &ConsultaWidget::aplicarFiltro);
    connect(m_tabelaCadastros, &QTableWidget::cellClicked, this, &ConsultaWidget::aoSelecionarCadastro);
}

void ConsultaWidget::recarregarCadastros()
{
    const auto cadastros = m_repositorio.listarCadastros(m_filtroAtual);
    atualizarTabelaCadastros(cadastros);
    if (!cadastros.isEmpty()) {
        aoSelecionarCadastro(0, 0);
        m_tabelaCadastros->selectRow(0);
    } else {
        atualizarTabelaLogs({});
    }
}

void ConsultaWidget::aplicarFiltro(const QString &texto)
{
    m_filtroAtual = texto;
    recarregarCadastros();
}

void ConsultaWidget::aoSelecionarCadastro(int linha, int /*coluna*/)
{
    if (linha < 0 || linha >= m_tabelaCadastros->rowCount()) {
        return;
    }

    const auto codigo = m_tabelaCadastros->item(linha, 0)->text();
    const auto logs = m_repositorio.listarLogsPorCadastro(codigo);
    atualizarTabelaLogs(logs);
}

void ConsultaWidget::atualizarTabelaCadastros(const QVector<Cadastro> &cadastros)
{
    m_tabelaCadastros->setRowCount(cadastros.size());
    for (int i = 0; i < cadastros.size(); ++i) {
        const auto &cadastro = cadastros.at(i);
        m_tabelaCadastros->setItem(i, 0, new QTableWidgetItem(cadastro.codigo));
        m_tabelaCadastros->setItem(i, 1, new QTableWidgetItem(cadastro.nome));
        m_tabelaCadastros->setItem(i, 2, new QTableWidgetItem(cadastro.email));
        m_tabelaCadastros->setItem(i, 3, new QTableWidgetItem(
            QStringLiteral("R$ %1").arg(QString::number(cadastro.renda, 'f', 2))
        ));
        m_tabelaCadastros->setItem(i, 4, new QTableWidgetItem(cadastro.status));
        m_tabelaCadastros->setItem(i, 5, new QTableWidgetItem(
            cadastro.criadoEm.toString("dd/MM/yyyy HH:mm")
        ));
    }
    m_tabelaCadastros->resizeRowsToContents();
}

void ConsultaWidget::atualizarTabelaLogs(const QVector<LogEnvio> &logs)
{
    m_tabelaLogs->setRowCount(logs.size());
    for (int i = 0; i < logs.size(); ++i) {
        const auto &log = logs.at(i);
        m_tabelaLogs->setItem(i, 0, new QTableWidgetItem(
            log.criadoEm.toString("dd/MM/yyyy HH:mm")
        ));
        m_tabelaLogs->setItem(i, 1, new QTableWidgetItem(log.modelo));
        m_tabelaLogs->setItem(i, 2, new QTableWidgetItem(log.statusEnvio));
        m_tabelaLogs->setItem(i, 3, new QTableWidgetItem(log.mensagem));
    }
    m_tabelaLogs->resizeRowsToContents();
}
