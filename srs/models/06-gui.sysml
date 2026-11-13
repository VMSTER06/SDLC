package GuiLib {
    // Библиотека элементов графического интерфейса для мокапов (вид InterconnectionView)
    private import ScalarValues::*;
    abstract part def Widget;
    part def Window :> Widget { attribute caption : String; }
    part def Panel :> Widget { attribute layout : String; attribute weights : Integer[*]; }
    part def Card :> Panel;
    part def TabBar :> Widget { attribute tabs : String[*]; attribute selected : Integer; }
    part def Button :> Widget { attribute text : String; attribute primary : Boolean; }
    part def Label :> Widget { attribute text : String; attribute big : Boolean; }
    part def Note :> Widget { attribute lines : String[*]; }
    part def ComboBox :> Widget { attribute value : String; }
    part def TextField :> Widget { attribute placeholder : String; }
    part def CheckBox :> Widget { attribute text : String; attribute checked : Boolean; }
    part def Toggle :> Widget { attribute text : String; attribute hint : String; attribute on : Boolean; }
    part def Table :> Widget {
        attribute columns : String[*];
        attribute widths : Integer[*];
        attribute rows : String[*];      // ячейки строки разделяются символом |
        attribute highlight : Integer[*];
    }
    part def Indicator :> Widget { attribute text : String; }
    part def Scale :> Widget { attribute progress : Integer; }
    part def StatusBar :> Widget { attribute text : String; }
    part def Menu :> Widget { attribute items : String[*]; }
    part def Notification :> Widget { attribute title : String; attribute text : String; }

    // Данные, передаваемые между элементами окна
    connection def OperationProgress { end part source; end part target; }
    connection def ConnectionState { end part source; end part target; }
    connection def SelectedProfile { end part source; end part target; }
    connection def SavedOptions { end part source; end part target; }
}

package GuiMockups {
    private import GuiLib::*;

    // UI-01 — главное окно, страница «Подключение» (REQ-INT-001, REQ-INT-002, REQ-FUNC-001, REQ-FUNC-005)
    part mainWindow : Window {
        :>> caption = "Murik DNS — Подключение";
        part navigation : TabBar {
            :>> tabs = ("Подключение", "Настройки", "В трей");
            :>> selected = 1;
        }
        part connectionCard : Card {
            :>> layout = "center";
            part lblState : Indicator { :>> text = "ПОДКЛЮЧЕНО"; }
            part lblProfile : Label { :>> text = "Zapret DNS (Нидерланды)"; :>> big = true; }
            part lblAddress : Label { :>> text = "83.217.211.149 / DoH"; }
            part btnBest : Button { :>> text = "Подобрать и подключить"; :>> primary = true; }
            part btnDisconnect : Button { :>> text = "Отключить"; }
            part scale : Scale { :>> progress = 92; }
        }
        part bottomBar : Panel {
            :>> layout = "row";
            :>> weights = (3, 1);
            part btnServers : Button { :>> text = "DNS-серверы и исключения →"; }
            part btnManual : Button { :>> text = "Выбрать DNS вручную"; }
        }
        part statusBar : StatusBar { :>> text = "Текущие DNS и DoH подтверждены."; }
        connection : OperationProgress connect connectionCard.btnBest to connectionCard.scale;
        connection : ConnectionState connect connectionCard to statusBar;
    }

    // UI-02 — настройки, вкладка «DNS-серверы» (REQ-INT-003, REQ-FUNC-006, REQ-FUNC-007, REQ-FUNC-008)
    part serversWindow : Window {
        :>> caption = "Murik DNS — Настройки";
        part navigation : TabBar {
            :>> tabs = ("Подключение", "Настройки", "В трей");
            :>> selected = 2;
        }
        part sections : TabBar {
            :>> tabs = ("DNS-серверы", "Подключение и запуск");
            :>> selected = 1;
        }
        part body : Panel {
            :>> layout = "row";
            :>> weights = (3, 1);
            part serverList : Panel {
                part tblServers : Table {
                    :>> columns = ("DNS", "Пинг", "DNS", "ChatGPT", "Claude", "Результат", "Исключить");
                    :>> widths = (6, 2, 2, 3, 3, 3, 3);
                    :>> rows = ("GeoHide Europe|92|829|642|604|Лучший #1|[ ]",
                                "GeoHide Europe — резерв|114|1286|439|373|Лучший #2|[ ]",
                                "Bezmezhau — резерв|76|979|589|597|Лучший #3|[ ]",
                                "Bezmezhau DNS (Беларусь)|83|951|676|573|Доступен|[ ]",
                                "Astracat / Commonnet|–|1132|586|525|Доступен|[ ]",
                                "Comss.one — фильтрация|49|940|1773|1153|Доступен|[x]",
                                "Malw DNS|–|–|–|–|Недоступен|[ ]");
                    :>> highlight = (1, 2, 3);
                }
                part note : Note {
                    :>> lines = ("Проверено: 29.10 10:23 · Лучший: GeoHide Europe (REQ-FUNC-008)",
                                 "Задержки в миллисекундах; «–» — нет ответа",
                                 "Отметка «Исключить» убирает DNS только из подбора (REQ-FUNC-007)",
                                 "Выбор строки задаёт профиль в панели «Вручную» (REQ-FUNC-006)");
                }
            }
            part manualPanel : Card {
                part cbProfile : ComboBox { :>> value = "Zapret DNS (Нидерланды)"; }
                part cbAdapter : ComboBox { :>> value = "Беспроводная сеть"; }
                part btnConnect : Button { :>> text = "Подключить"; :>> primary = true; }
                part btnRefresh : Button { :>> text = "Обновить сеть"; }
            }
        }
        part statusBar : StatusBar { :>> text = "Проверено 15 профилей, доступно 13."; }
        connection : SelectedProfile connect body.serverList.tblServers to body.manualPanel.cbProfile;
    }

    // UI-03 — настройки, вкладка «Подключение и запуск» (REQ-FUNC-009…011, REQ-FUNC-013, REQ-FUNC-014)
    part optionsWindow : Window {
        :>> caption = "Murik DNS — Настройки";
        part navigation : TabBar {
            :>> tabs = ("Подключение", "Настройки", "В трей");
            :>> selected = 2;
        }
        part sections : TabBar {
            :>> tabs = ("DNS-серверы", "Подключение и запуск");
            :>> selected = 2;
        }
        part tglTheme : Toggle { :>> text = "Тёмная тема"; :>> hint = "Сохраняется сразу."; :>> on = true; }
        part groups : Panel {
            :>> layout = "row";
            :>> weights = (1, 1);
            part launchGroup : Card {
                part tglStartup : Toggle { :>> text = "Запуск с Windows"; :>> hint = "После входа в систему."; :>> on = true; }
                part tglHidden : Toggle { :>> text = "Запускать в трее"; :>> hint = "Без открытия окна."; :>> on = true; }
                part tglAutoConnect : Toggle { :>> text = "Подключаться при запуске"; :>> hint = "Сохранённый DNS без подбора."; :>> on = true; }
            }
            part networkGroup : Card {
                part tglReconnect : Toggle { :>> text = "Восстанавливать подключение"; :>> hint = "После потери связи."; :>> on = true; }
                part tglFollow : Toggle { :>> text = "Переходить на активную сеть"; :>> hint = "Смена Wi-Fi или Ethernet."; :>> on = true; }
                part tglIpv6 : Toggle { :>> text = "Отключать IPv6"; :>> hint = "Восстанавливается при отключении."; :>> on = true; }
            }
        }
        part btnSave : Button { :>> text = "Сохранить настройки"; :>> primary = true; }
        connection : SavedOptions connect groups to btnSave;
    }

    // UI-04 — значок в трее и уведомление (REQ-FUNC-012, REQ-FUNC-016)
    part trayArea : Window {
        :>> caption = "Область уведомлений Windows";
        part tray : Panel {
            :>> layout = "row";
            :>> weights = (1, 2);
            part trayMenu : Menu { :>> items = ("Открыть", "Отключить DNS", "Выход"); }
            part toast : Notification {
                :>> title = "Murik DNS 3.0.1";
                :>> text = "Подключён Zapret DNS (Нидерланды) после смены сети";
            }
        }
        part note : Note {
            :>> lines = ("Подсказка значка: «Murik DNS 3.0.1»",
                         "«Выход» завершает программу без отключения DNS (REQ-FUNC-012)",
                         "Уведомление показывается при действиях без участия пользователя (REQ-FUNC-016)");
        }
    }
}
