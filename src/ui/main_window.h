#pragma once

#include <QMainWindow>

class QAction;
class QMenu;

namespace assinador::ui {

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
    void conectarSinais();

    QMenu *m_menuCadastro {nullptr};
    QMenu *m_menuConsulta {nullptr};
    QAction *m_acaoNovoCadastro {nullptr};
    QAction *m_acaoConsultarRegistros {nullptr};
};

} // namespace assinador::ui
