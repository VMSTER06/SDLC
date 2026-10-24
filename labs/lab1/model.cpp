#include "model.h"

Model::Model(QObject *parent) : QObject(parent)
{
}

bool Model::setInputData(int years, double hoursPerDay,
                         QString &errorMessage)
{
    if (years <= 0 || years > 120) {
        errorMessage = QStringLiteral(
            "Количество лет должно быть в диапазоне от 1 до 120.");
        return false;
    }
    if (hoursPerDay <= 0.0 || hoursPerDay > 24.0) {
        errorMessage = QStringLiteral(
            "Количество часов в день должно быть в диапазоне "
            "от 0 до 24.");
        return false;
    }

    m_stats.years = years;
    m_stats.hoursPerDay = hoursPerDay;
    recalculate();

    emit dataChanged(m_stats);
    return true;
}

void Model::recalculate()
{
    m_stats.totalHours =
        m_stats.years * DAYS_PER_YEAR * m_stats.hoursPerDay;
    m_stats.totalDays = m_stats.totalHours / 24.0;
    m_stats.cursorMileageKm = m_stats.totalHours * CURSOR_KM_PER_HOUR;
    m_stats.clicksCount =
        static_cast<qint64>(m_stats.totalHours * CLICKS_PER_HOUR);
    m_stats.keystrokesCount =
        static_cast<qint64>(m_stats.totalHours * KEYSTROKES_PER_HOUR);
}
