#include <QApplication>

#include "controller.h"
#include "mainwindow.h"
#include "model.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    Model model;
    MainWindow view;
    Controller controller(&model, &view);

    view.resize(420, 320);
    view.show();

    return app.exec();
}
