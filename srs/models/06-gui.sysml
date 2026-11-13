package GuiLib {
    // Библиотека элементов графического интерфейса для мокапов
    private import ScalarValues::String;
    part def 'Окно';
    part def 'Меню' { attribute 'пункты' : String[*]; }
    part def 'Навигация' { attribute 'кнопки' : String[*]; }
    part def 'Панель' { attribute 'кнопки' : String[*]; }
    part def 'Карточка';
    part def 'Надпись';
    part def 'Кнопка';
    part def 'Выпадающий список';
    part def 'Таблица' { attribute 'столбцы' : String[*]; }
    part def 'Переключатель';
    part def 'Индикатор';
    part def 'Строка состояния';
    // Связи между элементами окна (передаваемые данные)
    connection def 'Выбранный профиль' { end part 'откуда'; end part 'куда'; }
    connection def 'Результаты подбора' { end part 'откуда'; end part 'куда'; }
    connection def 'Состояние подключения' { end part 'откуда'; end part 'куда'; }
    connection def 'Ход операции' { end part 'откуда'; end part 'куда'; }
}

package GuiMockups {
    private import GuiLib::*;
    // Нетипизированная связь connect задаёт порядок обхода клавишей Tab
    // (сверху вниз); типизированная связь показывает передачу данных.

    part <home> 'Главное окно — страница «Подключение»' : 'Окно' {
        part <nav> 'Верхняя навигация' : 'Навигация' {
            attribute redefines 'кнопки' = ("Подключение", "Настройки", "В трей");
        }
        part <card> 'Карточка подключения' : 'Карточка' {
            part <state> 'Состояние: ПОДКЛЮЧЕНО / ОТКЛЮЧЕНО' : 'Индикатор';
            part <name> 'Название профиля DNS' : 'Надпись';
            part <addr> 'Адрес / DoH или DNS' : 'Надпись';
            part <best> 'Подобрать и подключить' : 'Кнопка';
            part <off> 'Отключить' : 'Кнопка';
            part <scale> 'Шкала хода проверки' : 'Индикатор';
            connect best to off;
            connection : 'Ход операции' connect best to scale;
        }
        part <links> 'Нижняя панель' : 'Панель' {
            attribute redefines 'кнопки' = ("DNS-серверы и исключения →", "Выбрать DNS вручную");
        }
        part <status> 'Строка сообщений' : 'Строка состояния';
        connect nav to card;
        connect card to links;
        connection : 'Состояние подключения' connect card to status;
    }

    part <servers> 'Настройки — вкладка «DNS-серверы»' : 'Окно' {
        part <tabs> 'Вкладки настроек' : 'Навигация' {
            attribute redefines 'кнопки' = ("DNS-серверы", "Подключение и запуск");
        }
        part <table> 'Таблица серверов' : 'Таблица' {
            attribute redefines 'столбцы' = ("DNS", "Пинг", "DNS, мс", "ChatGPT, мс", "Claude, мс", "Результат", "Исключить");
        }
        part <manual> 'Панель «Вручную»' : 'Карточка' {
            part <profile> 'DNS' : 'Выпадающий список';
            part <adapter> 'Сеть' : 'Выпадающий список';
            part <connectBtn> 'Подключить' : 'Кнопка';
            part <refresh> 'Обновить сеть' : 'Кнопка';
            connect profile to adapter;
            connect adapter to connectBtn;
            connect connectBtn to refresh;
        }
        connect tabs to table;
        connect table to manual;
        connection : 'Выбранный профиль' connect table to manual;
    }

    part <options> 'Настройки — вкладка «Подключение и запуск»' : 'Окно' {
        part <tabs> 'Вкладки настроек' : 'Навигация' {
            attribute redefines 'кнопки' = ("DNS-серверы", "Подключение и запуск");
        }
        part <look> 'Тёмная тема (сохраняется сразу)' : 'Переключатель';
        part <launch> 'Группа «Запуск»' : 'Карточка' {
            part <withWin> 'Запуск с Windows' : 'Переключатель';
            part <hidden> 'Запускать в трее' : 'Переключатель';
            part <autoConn> 'Подключаться при запуске' : 'Переключатель';
            connect withWin to hidden;
            connect hidden to autoConn;
        }
        part <net> 'Группа «Сеть»' : 'Карточка' {
            part <reconn> 'Восстанавливать подключение' : 'Переключатель';
            part <follow> 'Переходить на активную сеть' : 'Переключатель';
            part <v6> 'Отключать IPv6' : 'Переключатель';
            connect reconn to follow;
            connect follow to v6;
        }
        part <save> 'Сохранить настройки' : 'Кнопка';
        connect tabs to look;
        connect look to launch;
        connect launch to net;
        connect net to save;
    }

    part <trayMenu> 'Значок в трее' : 'Меню' {
        attribute redefines 'пункты' = ("Открыть", "Отключить DNS", "Выход");
        part <tip> 'Подсказка «Murik DNS 3.0.1»' : 'Надпись';
    }
}

package GuiNavigation {
    // Карта переходов между окнами (связь — переход по действию пользователя)
    part <winmap> 'Карта окон Murik DNS' {
        part <w0> 'Запуск (запрос прав администратора)';
        part <w1> 'Главное окно «Подключение»';
        part <w2> 'Настройки: DNS-серверы';
        part <w3> 'Настройки: Подключение и запуск';
        part <w4> 'Значок в трее';
        connect w0 to w1;
        connect w0 to w4;
        connect w1 to w2;
        connect w2 to w3;
        connect w1 to w4;
        connect w4 to w1;
    }
}
