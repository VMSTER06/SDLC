#pragma once

#include <QDialog>

class QLineEdit;

// Диалоговое окно ввода данных (элемент View).
class InputDialog : public QDialog
{
    Q_OBJECT
public:
    explicit InputDialog(QWidget *parent = nullptr);

    // Предзаполняет поля последними введёнными значениями.
    void setInitialValues(int years, double hoursPerDay);

    QString yearsText() const;
    QString hoursPerDayText() const;

private:
    QLineEdit *m_yearsEdit;
    QLineEdit *m_hoursEdit;
};
