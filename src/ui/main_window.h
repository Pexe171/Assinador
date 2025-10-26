#pragma once

#include <QMainWindow>

class QAction;
class QMenu;
class QTabWidget;

namespace assinador::ui {

class CadastroForm;
class ConsultaWidget;

/**
 * @brief Janela principal responsável por exibir menus de cadastro e consulta.
 */
class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override = default;

private:
    void criarMenus();
    void criarConteudoCentral();
    void conectarSinais();

    QMenu *m_menuCadastro {nullptr};
    QMenu *m_menuConsulta {nullptr};
    QAction *m_acaoNovoCadastro {nullptr};
    QAction *m_acaoConsultarRegistros {nullptr};
    QTabWidget *m_tabs {nullptr};
    CadastroForm *m_cadastroForm {nullptr};
    ConsultaWidget *m_consultaWidget {nullptr};
};

} // namespace assinador::ui
