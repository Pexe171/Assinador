#include "data/database_manager.h"
#include "integration/outlook_automation.h"
#include "ui/main_window.h"

#include <QApplication>

#include <cstdlib>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    auto &db = assinador::data::DatabaseManager::instance();
    if (!db.abrirConexao()) {
        return EXIT_FAILURE;
    }

    assinador::integration::OutlookAutomation outlook;
    Q_UNUSED(outlook);

    assinador::ui::MainWindow janela;
    janela.show();

    const auto resultado = app.exec();
    db.fecharConexao();
    return resultado;
}
