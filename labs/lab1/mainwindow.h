#pragma once

#include <QMainWindow>

#include "model.h"

class QLabel;
class QPushButton;

// Главное окно (View). Ничего не знает о Controller напрямую:
// сообщает о действии пользователя сигналом enterDataRequested
// и подписывается на изменения активной модели (onModelDataChanged).
class MainWindow : public QMainWindow
{
    Q_OBJECT
public:
    explicit MainWindow(QWidget *parent = nullptr);

signals:
    void enterDataRequested();

public slots:
    void onModelDataChanged(const LifeStats &stats);

private:
    QLabel *m_inputSummaryLabel;
    QLabel *m_totalHoursLabel;
    QLabel *m_totalDaysLabel;
    QLabel *m_cursorMileageLabel;
    QLabel *m_clicksLabel;
    QLabel *m_keystrokesLabel;
    QPushButton *m_enterDataButton;
};
