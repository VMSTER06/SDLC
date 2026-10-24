package LifeCalculator {

    doc /*
     * Модель системы «Калькулятор Жизни» (вариант 14)
     * в текстовой нотации SysML v2.
     */

    // --- Типы данных -----------------------------------------------------

    attribute def RawLifeInput {
        doc /* «Сырые» данные из окна ввода: хранятся строками, чтобы
             * проверку выполняла модель, а не элементы интерфейса. */
        attribute yearsText : String;
        attribute hoursPerDayText : String;
    }

    attribute def LifeStats {
        doc /* Принятые моделью данные и результаты расчёта. */
        attribute years : Integer;
        attribute hoursPerDay : Real;
        attribute totalHours : Real;
        attribute totalDays : Real;
        attribute cursorMileageKm : Real;
        attribute clicksCount : Integer;
        attribute keystrokesCount : Integer;
    }

    // --- Структура системы ----------------------------------------------

    part def ModelLayer {
        attribute stats : LifeStats;
        port notify : NotificationPort;
    }

    part def ViewLayer {
        port observe : ~NotificationPort;
    }

    part def ControllerLayer;

    port def NotificationPort {
        out item dataChanged : LifeStats;
    }

    part def Application {
        part model : ModelLayer;
        part view : ViewLayer;
        part controller : ControllerLayer;

        // Активная модель: уведомление идёт от модели к представлению
        // напрямую, минуя контроллер.
        connect model.notify to view.observe;
    }

    // --- Поведение -------------------------------------------------------

    action def CalculateLifeStats {
        in raw : RawLifeInput;
        out stats : LifeStats;

        action remember;      // запомнить последний ввод
        action validate;      // проверить диапазоны
        action recalculate;   // пересчитать показатели
        action notify;        // разослать уведомление наблюдателям

        first remember then validate;
        succession validate then recalculate;
        succession recalculate then notify;
    }

    // --- Требования варианта 14 ------------------------------------------

    requirement def <R1> EnterDataButton {
        doc /* На главной форме размещена кнопка «Ввести данные». */
    }

    requirement def <R2> SeparateInputWindow {
        doc /* Ввод данных выполняется в отдельном окне. */
    }

    requirement def <R3> RestoreLastInput {
        doc /* Последние введённые данные запоминаются и восстанавливаются
             * при повторном открытии окна ввода. */
    }

    requirement def <R4> ShowResults {
        doc /* Результаты расчёта отображаются на главной форме. */
    }

    requirement def <R5> ErrorMessage {
        doc /* При некорректных данных выводится сообщение об ошибке. */
    }

    requirement def <R6> ActiveModelMvc {
        doc /* Реализован каркас MVC с активной моделью. */
    }

    part variant14 : Application {
        satisfy requirement :>> EnterDataButton;
        satisfy requirement :>> SeparateInputWindow;
        satisfy requirement :>> RestoreLastInput;
        satisfy requirement :>> ShowResults;
        satisfy requirement :>> ErrorMessage;
        satisfy requirement :>> ActiveModelMvc;
    }
}
