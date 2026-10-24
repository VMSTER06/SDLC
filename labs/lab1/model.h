#pragma once

#include <QObject>
#include <QString>

// Результаты расчёта "Калькулятора Жизни" за компьютером.
struct LifeStats
{
    int years = 0;
    double hoursPerDay = 0.0;

    double totalHours = 0.0;
    double totalDays = 0.0;
    double cursorMileageKm = 0.0;
    qint64 clicksCount = 0;
    qint64 keystrokesCount = 0;
};

// Активная модель: сама валидирует и пересчитывает данные,
// и уведомляет подписчиков (View) сигналом dataChanged об изменениях.
class Model : public QObject
{
    Q_OBJECT
public:
    explicit Model(QObject *parent = nullptr);

    // Проверяет данные и, если они корректны, обновляет состояние
    // и рассылает сигнал dataChanged. При ошибке возвращает false
    // и заполняет errorMessage.
    bool setInputData(int years, double hoursPerDay, QString &errorMessage);

    const LifeStats &stats() const { return m_stats; }

signals:
    void dataChanged(const LifeStats &stats);

private:
    // Усреднённые статистические коэффициенты для пользователя ПК:
    // дистанция перемещения курсора, клики и нажатия клавиш в час.
    static constexpr double DAYS_PER_YEAR = 365.25;
    static constexpr double CURSOR_KM_PER_HOUR = 0.15;
    static constexpr double CLICKS_PER_HOUR = 800.0;
    static constexpr double KEYSTROKES_PER_HOUR = 3000.0;

    LifeStats m_stats;

    void recalculate();
};
