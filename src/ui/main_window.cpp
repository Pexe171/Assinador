#include "main_window.h"

#include <QAction>
#include <QMenu>
#include <QMenuBar>
#include <QStatusBar>

using namespace assinador::ui;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setWindowTitle(tr("Assinador - Gestão de Cadastros"));
    resize(960, 600);

    criarMenus();
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

void MainWindow::conectarSinais()
{
    connect(m_acaoNovoCadastro, &QAction::triggered, this, [this]() {
        statusBar()->showMessage(tr("Fluxo de cadastro será implementado em breve."));
    });

    connect(m_acaoConsultarRegistros, &QAction::triggered, this, [this]() {
        statusBar()->showMessage(tr("Fluxo de consulta será implementado em breve."));
    });
}
