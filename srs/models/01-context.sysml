package MurikContext {
    doc /* Системный контекст ПО «Murik DNS» */
    part def 'Программное средство';
    part def 'Пользователь';
    part def 'Компонент Windows';
    part def 'Внешний сервис';
    part def 'Хранилище';

    part <context> 'Контекст Murik DNS' {
        part <user> 'Пользователь ПК' : 'Пользователь';
        part <sys> 'ПО Murik DNS (Windows 11 x64)' : 'Программное средство';
        part <net> 'Сетевые настройки Windows (DNS, DoH, IPv6)' : 'Компонент Windows';
        part <sched> 'Планировщик заданий Windows' : 'Компонент Windows';
        part <tray> 'Область уведомлений (трей)' : 'Компонент Windows';
        part <dns> 'DNS-провайдеры (15 профилей)' : 'Внешний сервис';
        part <ai> 'Проверяемые сервисы chatgpt.com, claude.ai' : 'Внешний сервис';
        part <store> 'Файлы настроек и журнала %LOCALAPPDATA%' : 'Хранилище';

        connection 'подбор, подключение, настройки' connect user to sys;
        connection 'чтение и изменение адаптеров' connect sys to net;
        connection 'автозапуск' connect sys to sched;
        connection 'значок и меню' connect sys to tray;
        connection 'DNS- и DoH-запросы, ping' connect sys to dns;
        connection 'HTTPS /cdn-cgi/trace' connect sys to ai;
        connection 'чтение / запись JSON' connect sys to store;
    }
}
