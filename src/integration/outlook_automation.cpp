#include "integration/outlook_automation.h"

#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>
#include <QTextStream>

#ifdef Q_OS_WIN
#    include <QAxObject>
#endif

namespace assinador::integration {

OutlookAutomation::OutlookAutomation(QString diretorioModelos)
    : m_diretorioModelos(std::move(diretorioModelos))
{
    if (m_diretorioModelos.isEmpty()) {
        const auto basePath = QCoreApplication::applicationDirPath();
        QDir resourcesDir(basePath);
        m_diretorioModelos = resourcesDir.filePath("resources/oft");
    }
}

bool OutlookAutomation::enviarModelo(const QString &nomeModelo, const QMap<QString, QString> &placeholders)
{
    const auto caminho = resolverCaminhoModelo(nomeModelo);
    QFileInfo info(caminho);
    if (!info.exists()) {
        QTextStream(stderr) << "Modelo OFT não encontrado: " << caminho << '\n';
        return false;
    }

#ifndef Q_OS_WIN
    QTextStream(stderr) << "Integração com Outlook disponível apenas no Windows." << '\n';
    return false;
#else
    QAxObject outlook("Outlook.Application");
    auto *mailItem = outlook.querySubObject("CreateItemFromTemplate(const QString&)", caminho);
    if (!mailItem) {
        QTextStream(stderr) << "Não foi possível abrir o modelo OFT no Outlook." << '\n';
        return false;
    }

    QString htmlBody = mailItem->property("HTMLBody").toString();
    for (auto it = placeholders.cbegin(); it != placeholders.cend(); ++it) {
        htmlBody.replace(it.key(), it.value());
    }
    mailItem->setProperty("HTMLBody", htmlBody);

    mailItem->dynamicCall("Display()");
    delete mailItem;
    return true;
#endif
}

QString OutlookAutomation::diretorioModelos() const
{
    return m_diretorioModelos;
}

void OutlookAutomation::definirDiretorioModelos(const QString &diretorio)
{
    m_diretorioModelos = diretorio;
}

QString OutlookAutomation::resolverCaminhoModelo(const QString &nomeModelo) const
{
    QFileInfo info(nomeModelo);
    if (info.isAbsolute()) {
        return info.absoluteFilePath();
    }

    QDir dir(m_diretorioModelos);
    return dir.filePath(nomeModelo);
}

} // namespace assinador::integration
