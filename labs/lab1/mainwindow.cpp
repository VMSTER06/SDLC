#include "mainwindow.h"

#include <QFormLayout>
#include <QGroupBox>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QWidget>

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent)
{
    setWindowTitle(tr("Калькулятор Жизни"));

    m_inputSummaryLabel = new QLabel(tr("Данные ещё не введены"), this);
    m_totalHoursLabel = new QLabel(tr("—"), this);
    m_totalDaysLabel = new QLabel(tr("—"), this);
    m_cursorMileageLabel = new QLabel(tr("—"), this);
    m_clicksLabel = new QLabel(tr("—"), this);
    m_keystrokesLabel = new QLabel(tr("—"), this);
    m_enterDataButton = new QPushButton(tr("Ввести данные"), this);

    auto *resultsGroup = new QGroupBox(tr("Результаты"), this);
    auto *formLayout = new QFormLayout;
    formLayout->addRow(tr("Часов за компьютером всего:"),
                       m_totalHoursLabel);
    formLayout->addRow(tr("Суток за компьютером:"), m_totalDaysLabel);
    formLayout->addRow(tr("Пробег курсора, км:"), m_cursorMileageLabel);
    formLayout->addRow(tr("Кликов мышью:"), m_clicksLabel);
    formLayout->addRow(tr("Нажатий клавиш:"), m_keystrokesLabel);
    resultsGroup->setLayout(formLayout);

    auto *central = new QWidget(this);
    auto *mainLayout = new QVBoxLayout(central);
    mainLayout->addWidget(m_inputSummaryLabel);
    mainLayout->addWidget(m_enterDataButton);
    mainLayout->addWidget(resultsGroup);
    mainLayout->addStretch(1);
    setCentralWidget(central);

    connect(m_enterDataButton, &QPushButton::clicked,
            this, &MainWindow::enterDataRequested);
}

void MainWindow::onModelDataChanged(const LifeStats &stats)
{
    m_inputSummaryLabel->setText(
        tr("Введено: %1 лет, %2 ч/день за компьютером")
            .arg(stats.years)
            .arg(stats.hoursPerDay));

    m_totalHoursLabel->setText(QString::number(stats.totalHours, 'f', 1));
    m_totalDaysLabel->setText(QString::number(stats.totalDays, 'f', 1));
    m_cursorMileageLabel->setText(
        QString::number(stats.cursorMileageKm, 'f', 2));
    m_clicksLabel->setText(QString::number(stats.clicksCount));
    m_keystrokesLabel->setText(QString::number(stats.keystrokesCount));
}
