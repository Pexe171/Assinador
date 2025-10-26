#include "main_window.h"

#include "cadastro_form.h"
#include "consulta_widget.h"

#include <QAction>
#include <QMenu>
#include <QMenuBar>
#include <QStatusBar>
#include <QTabWidget>

using namespace assinador::ui;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setWindowTitle(tr("Assinador - Gestão de Cadastros"));
    resize(960, 600);

    criarMenus();
    criarConteudoCentral();
    conectarSinais();

    statusBar()->showMessage(tr("Pronto para cadastrar ou consultar."));
}

void MainWindow::criarMenus()
{
    auto *barra = menuBar();
    m_menuCadastro = barra->addMenu(tr("Cadastro"));
    m_menuConsulta = barra->addMenu(tr("Consulta"));

    m_acaoNovoCadastro = m_menuCadastro->addAction(tr("Novo cadastro"));
    m_acaoConsultarRegistros = m_menuConsulta->addAction(tr("Consultar registros"));
}

void MainWindow::criarConteudoCentral()
{
    m_tabs = new QTabWidget(this);
    m_cadastroForm = new CadastroForm(this);
    m_consultaWidget = new ConsultaWidget(this);

    m_tabs->addTab(m_cadastroForm, tr("Cadastro"));
    m_tabs->addTab(m_consultaWidget, tr("Consulta"));

    setCentralWidget(m_tabs);
}

void MainWindow::conectarSinais()
{
    connect(m_acaoNovoCadastro, &QAction::triggered, this, [this]() {
        m_tabs->setCurrentWidget(m_cadastroForm);
        statusBar()->showMessage(tr("Formulário de cadastro ativo."));
    });

    connect(m_acaoConsultarRegistros, &QAction::triggered, this, [this]() {
        m_tabs->setCurrentWidget(m_consultaWidget);
        m_consultaWidget->recarregarCadastros();
        statusBar()->showMessage(tr("Listagem de cadastros atualizada."));
    });

    connect(m_cadastroForm, &CadastroForm::cadastroCriado, this, [this](const auto &cadastro) {
        statusBar()->showMessage(tr("Cadastro %1 salvo com sucesso.").arg(cadastro.codigo));
        m_consultaWidget->recarregarCadastros();
    });
}
