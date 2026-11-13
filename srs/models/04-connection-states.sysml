package ConnectionStates {
    doc /* Жизненный цикл подключения DNS */
    item def 'Подобрать и подключить';
    item def 'Подключить вручную';
    item def 'Подбор завершён';
    item def 'Настройки применены';
    item def 'Ошибка применения';
    item def 'Сеть потеряна или сменилась';
    item def 'Сеть стабильна';
    item def 'Отключить';
    item def 'Исходные настройки восстановлены';

    state def <ConnState> 'Состояние подключения' {
        entry; then off;
        state <off> 'Отключено';
        state <probing> 'Подбор DNS';
        state <applying> 'Применение настроек';
        state <on> 'Подключено';
        state <waiting> 'Ожидание сети';
        state <restoring> 'Восстановление оригинала';

        transition first off accept : 'Подобрать и подключить' then probing;
        transition first on accept : 'Подобрать и подключить' then probing;
        transition first off accept : 'Подключить вручную' then applying;
        transition first probing accept : 'Подбор завершён' then applying;
        transition first applying accept : 'Настройки применены' then on;
        transition first applying accept : 'Ошибка применения' then restoring;
        transition first on accept : 'Сеть потеряна или сменилась' then waiting;
        transition first waiting accept : 'Сеть стабильна' then applying;
        transition first on accept : 'Отключить' then restoring;
        transition first probing accept : 'Отключить' then restoring;
        transition first waiting accept : 'Отключить' then restoring;
        transition first restoring accept : 'Исходные настройки восстановлены' then off;
    }
}
