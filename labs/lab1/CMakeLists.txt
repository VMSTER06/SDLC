cmake_minimum_required(VERSION 3.16)

project(LifeCalculatorMVC LANGUAGES CXX)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets)

add_executable(LifeCalculatorMVC
    main.cpp
    model.h
    model.cpp
    mainwindow.h
    mainwindow.cpp
    inputdialog.h
    inputdialog.cpp
    controller.h
    controller.cpp
)

target_link_libraries(LifeCalculatorMVC
    PRIVATE Qt${QT_VERSION_MAJOR}::Widgets)

if(MSVC)
    target_compile_options(LifeCalculatorMVC PRIVATE /utf-8)
endif()
