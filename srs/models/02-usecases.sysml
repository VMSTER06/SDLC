package MurikUseCases {
    // Варианты использования ПО Murik DNS
    private import MurikContext::*;

    use case def <UC1> 'ВИ-1 Подобрать и подключить лучший DNS' {
        subject 'ПО Murik DNS' : 'Программное средство';
        actor 'Пользователь ПК' : 'Пользователь';
    }
    use case def <UC2> 'ВИ-2 Подключить DNS вручную' {
        subject 'ПО Murik DNS' : 'Программное средство';
        actor 'Пользователь ПК' : 'Пользователь';
    }
    use case def <UC3> 'ВИ-3 Отключить DNS и восстановить исходные настройки' {
        subject 'ПО Murik DNS' : 'Программное средство';
        actor 'Пользователь ПК' : 'Пользователь';
    }
    use case def <UC4> 'ВИ-4 Исключить DNS из подбора' {
        subject 'ПО Murik DNS' : 'Программное средство';
        actor 'Пользователь ПК' : 'Пользователь';
    }
    use case def <UC5> 'ВИ-5 Настроить запуск и восстановление' {
        subject 'ПО Murik DNS' : 'Программное средство';
        actor 'Пользователь ПК' : 'Пользователь';
    }
    use case def <UC6> 'ВИ-6 Восстановить подключение после смены сети' {
        subject 'ПО Murik DNS' : 'Программное средство';
        actor 'Сетевые настройки Windows' : 'Компонент Windows';
    }
}
