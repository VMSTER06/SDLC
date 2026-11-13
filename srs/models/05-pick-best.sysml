package PickBest {
    doc /* Сценарий «Подобрать и подключить» */
    private import ScalarValues::Boolean;

    action def <PickAndConnect> 'Подбор и подключение DNS' {
        // хотя бы один профиль прошёл DNS-запрос и обе HTTPS-проверки
        attribute 'есть доступный профиль' : Boolean;

        first start;
        then action <adapter> 'Определить активный сетевой адаптер и сеть';
        then action <probe> 'Параллельно проверить неисключённые профили: ping, DNS, HTTPS chatgpt.com и claude.ai (не более 8 с)';
        then action <rank> 'Отсеять недоступные, упорядочить по суммарной задержке, отметить «Лучший #1–3»';
        then decide;
            if 'есть доступный профиль' then backup;
            else fail;
        action <backup> 'Сохранить исходные DNS, DoH и IPv6 адаптера';
        then action <apply> 'Применить адреса и шаблон DoH лучшего профиля, сбросить кэш DNS';
        then action <remember> 'Запомнить результаты и лучший профиль для этой сети';
        then done;
        action <fail> 'Показать причину, настройки сети не изменять';
        then done;
    }
}
