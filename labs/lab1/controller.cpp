#include "controller.h"

#include <QMessageBox>

#include "inputdialog.h"
#include "mainwindow.h"
#include "model.h"

Controller::Controller(Model *model, MainWindow *view, QObject *parent)
    : QObject(parent), m_model(model), m_view(view)
{
    connect(m_view, &MainWindow::enterDataRequested,
            this, &Controller::onEnterDataRequested);
    connect(m_model, &Model::dataChanged,
            m_view, &MainWindow::onModelDataChanged);
}

void Controller::onEnterDataRequested()
{
    InputDialog dialog(m_view);
    const LifeStats &current = m_model->stats();
    dialog.setInitialValues(current.years, current.hoursPerDay);

    if (dialog.exec() != QDialog::Accepted)
        return;

    bool yearsOk = false;
    bool hoursOk = false;
    const int years = dialog.yearsText().toInt(&yearsOk);
    const double hours = dialog.hoursPerDayText().toDouble(&hoursOk);

    if (!yearsOk || !hoursOk) {
        QMessageBox::warning(m_view, tr("Ошибка ввода"),
                              tr("Введите корректные числовые значения."));
        return;
    }

    QString errorMessage;
    if (!m_model->setInputData(years, hours, errorMessage)) {
        QMessageBox::warning(m_view, tr("Ошибка ввода"), errorMessage);
    }
}
