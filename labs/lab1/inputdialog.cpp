#include "inputdialog.h"

#include <QDialogButtonBox>
#include <QFormLayout>
#include <QLineEdit>
#include <QVBoxLayout>

InputDialog::InputDialog(QWidget *parent) : QDialog(parent)
{
    setWindowTitle(tr("Ввод данных"));

    m_yearsEdit = new QLineEdit(this);
    m_hoursEdit = new QLineEdit(this);

    auto *formLayout = new QFormLayout;
    formLayout->addRow(tr("Количество лет:"), m_yearsEdit);
    formLayout->addRow(tr("Часов за компьютером в день:"), m_hoursEdit);

    auto *buttonBox = new QDialogButtonBox(
        QDialogButtonBox::Ok | QDialogButtonBox::Cancel, this);
    connect(buttonBox, &QDialogButtonBox::accepted, this, &QDialog::accept);
    connect(buttonBox, &QDialogButtonBox::rejected, this, &QDialog::reject);

    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->addLayout(formLayout);
    mainLayout->addWidget(buttonBox);
}

void InputDialog::setInitialValues(int years, double hoursPerDay)
{
    if (years > 0)
        m_yearsEdit->setText(QString::number(years));
    if (hoursPerDay > 0)
        m_hoursEdit->setText(QString::number(hoursPerDay));
}

QString InputDialog::yearsText() const
{
    return m_yearsEdit->text();
}

QString InputDialog::hoursPerDayText() const
{
    return m_hoursEdit->text();
}
