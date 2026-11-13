package GuiNavigation {
    // Карта переходов между окнами (связь — переход по действию пользователя)
    part <winmap> 'Карта окон Murik DNS' {
        part <w0> 'Запуск (запрос прав администратора)';
        part <w1> 'UI-01 Главное окно «Подключение»';
        part <w2> 'UI-02 Настройки: DNS-серверы';
        part <w3> 'UI-03 Настройки: Подключение и запуск';
        part <w4> 'UI-04 Значок в трее';
        connect w0 to w1;
        connect w0 to w4;
        connect w1 to w2;
        connect w2 to w3;
        connect w1 to w4;
        connect w4 to w1;
    }
}
