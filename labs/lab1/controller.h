#pragma once

#include <QObject>

class Model;
class MainWindow;

// Controller связывает View и Model: реагирует на действия пользователя,
// передаёт "сырые" данные модели и показывает сообщения об ошибках.
// Обновление View выполняет сама Model через сигнал dataChanged
// (активная модель).
class Controller : public QObject
{
    Q_OBJECT
public:
    Controller(Model *model, MainWindow *view, QObject *parent = nullptr);

private slots:
    void onEnterDataRequested();

private:
    Model *m_model;
    MainWindow *m_view;
};
