#pragma once

#include <QMap>
#include <QString>

namespace assinador::integration {

/**
 * @brief Serviço responsável por acionar modelos Outlook (.oft) via COM.
 */
class OutlookAutomation {
public:
    explicit OutlookAutomation(QString diretorioModelos = {});

    bool enviarModelo(const QString &nomeModelo, const QMap<QString, QString> &placeholders = {});

    [[nodiscard]] QString diretorioModelos() const;
    void definirDiretorioModelos(const QString &diretorio);

private:
    QString resolverCaminhoModelo(const QString &nomeModelo) const;

    QString m_diretorioModelos;
};

} // namespace assinador::integration
