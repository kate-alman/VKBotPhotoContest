from random import choice


class Const:
    GROUP_CHAT = 2000000000
    ROUND_TIME = 10


class Info:
    PERMISSION_REQUEST = (
        "Привет! Чтобы я начал работать, пожалуйста, дайте мне права администратора.<br>"
        "Если все готово, нажмите кнопку 'Активировать бота' или напишите 'start'."
    )
    INVITE_TO_START = (
        "Шестеренки закрутились! <br>"
        "Пожалуйста, убедитесь, что в чате более 3х участников и у всех есть аватарки (профили должны быть открыты).<br>"
        "Для старта нажмите 'Запустить конкурс' или напишите в чат 'starting'.<br>"
        "Чтобы получить более полную информацию о моих возможностях, нажмите 'Доступные команды' или напишите 'help'"
    )
    LAST_WINNER = "В последней битве за звание красавчика победил(-а) "
    EMPTY_WINNER = "Кажется, пьедестал еще свободен."
    BAD_USER_AMOUNT = "Для запуска конкурса необходимо более 2х участников."
    GAME_HELP = (
        f"Доступные команды/кнопки: <br>"
        f"{chr(9881)} starting/Запустить конкурс - запускает конкурс, если достаточно участников; <br>"
        f"{chr(9881)} help/Доступные команды - выводит подробную инструкцию о возможностях бота, которую Вы сейчас читаете; <br>"
        f"{chr(9881)} rules/Правила конкурса - выводит правила проведения конкурса; <br>"
        f"{chr(9881)} score/Победитель прошлой игры - показывает список активных участников - тех, кто еще не выбыл; <br>"
        f"{chr(9881)} stop/Закончить конкурс - досрочно заканчивает конкурс и "
        f"выбирает победителя из активных участников на момент остановки; <br>"
        f"{chr(9881)} Кнопка 'Долго не отвечаю? Тык сюда!' перезапускает игру с того места, на которой она зависла, <br>"
        f"например, из-за сбоя сервера или каких-то других причин. <br>"
        f"Кнопки голосования: <br>"
        f"{chr(9881)} Две верхние кнопки подписаны именами участников раунда и "
        f"соответствуют по порядку левому и правому участнику; <br>"
        f"{chr(9881)} Кнопка 'Пусть решит случай' случайно отдает голос за одного из участников раунда.<br>"
        f"Команды пишутся в чат без знаков препинания, кавычек и других символов."
    )
    GAME_RULES = (
        f"{chr(128220)} Бот помогает провести фотоконкурс. Участвуют все пользователи беседы, "
        f"у которых есть аватарки. <br>"
        f"{chr(128220)} Конкурс запускается только если участников более 2х. <br>"
        f"{chr(128220)} Когда конкурс запущен, начинаются раунды. Каждый раунд длится {Const.ROUND_TIME} секунд. <br>"
        f"В раунде участвуют два случайно выбранных пользователя из общего списка. <br>"
        f"По истечении времени, определяется победитель раунда, проигравший больше не участвует в конкурсе. <br>"
        f"{chr(128220)} Можно проголосовать не более одного раза в каждом раунде. <br>"
        f"Конкурс продолжается до тех пор, пока не останется один участник, "
        f"либо кто-то не остановит конкурс досрочно. <br>"
        f"{chr(128220)} После завершения конкурса можно начать его заново с обновленным списком участников. <br>"
        f"{chr(128220)} Подробно о доступных командах можно узнать, "
        f"нажав кнопку 'Доступные команды' или написав в чат 'help'"
    )
    GAME_ALREADY_RUNNING = (
        "Кто это у нас тут такой хитренький? Конкурс уже запущен.<br>"
        "Чтобы остановить конкурс, нажмите на кнопку 'Закончить конкурс' или напишите в чат 'stop'"
    )
    GAME_RERUN = "Конкурс перезапущен с момента, на котором остановился."
    ALREADY_VOTED = f"Ах ты шалунишка! Можно голосовать только один раз {chr(128521)}"
    STOP_GAME = "Кажется кто-то остановил игру, не завершив борьбу"
    GAME_ALREADY_STOP = "Игра уже завершена, её победитель: "
    CONGRAT = [
        f"И победителем {chr(10024)} становится... ",
        f"Кажется, с небес спустился ангел {chr(128124)}, и это... ",
        f"Я даже немного завидую твоей красоте {chr(129392)}, ",
        f"Вызывайте пожарных! {chr(128293)} Наш горячий победитель... ",
        f"Так-так-так, и где же прятался такой красивый человечек? {chr(128525)} Поздравляем с победой, ",
        f"Приз в студию! {chr(127873)} Ой... так вот же главный приз этого дня - ",
    ]
    ANNOUNCE_WINNER = f"{choice(CONGRAT)}"
    RANDOM_FACT = [
        "Ни один лист бумаги невозможно сложить пополам больше семи раз.",
        "Венера единственная планета Солнечной системы, вращающаяся против часовой стрелки.",
        "Пластмассовые штучки на концах шнурков называются аксельбанты.",
        "Утиное кряканье не дает эха, никто не знает почему.",
        "Женщины, в среднем, моргают вдвое чаще мужчин.",
        "Крокодилы не умеют высовывать язык.",
        "Туалетная бумага была изобретена в 1857 году.",
        "Тело спящего человека на полсантиметра длиннее, чем бодрствующего.",
        "Если 111.111.111 умножить на 111.111.111, то получится 12345678987654321.",
        "Слово 'врач' происходит от слова 'врать'. На Руси знахари часто лечили заговорами, заклинаниями. "
        "Бормотание, болтовня вплоть до начала XIX века назывались враньем.",
        "Самая сильная мышца в теле - это язык.",
        "Кипяток гасит огонь быстрее, чем холодная вода, так как сразу отнимает от пламени "
        "теплоту парообразования и окружает огонь слоем пара, затрудняющего доступ воздуха.",
        "",
    ]
    PRIVATE_CONVERSATION = (
        f"Я работаю только в беседах, пожалуйста, создайте беседу от 3х человек и пригласите меня, "
        f"а пока вот Вам интересный факт: <br> {choice(RANDOM_FACT)}<br>"
        f"Достоверность не гарантирую ;)"
    )
    START_MESSAGE = "Давайте посмотрим, кто тут главный красавчик!"
    LIST_ACTIVE_MEMBERS = "В борьбе за звание победителя участвуют: <br>"
    STATISTICS = "Статистика пользователей по победам: <br>"
    SOMETHING_BROKE = "Возникла ошибка: "
    # unused
    UNKNOWN_COMMAND = "Команда не опознана"
    PASS_VOTE = "Так и быть, я сделаю этот непростой выбор за тебя. Абракадабра!"
    SCORE_INFO = "На текущий момент дела обстоят так: ...."
    RERUN_GAME = "Кажется был какой-то сбой, пожалуйста, напишите starting в чат и нажмите кнопку заново"
    CLEAR_MEMBERS = "Список участников очищен, Вы можете заново запустить игру"
    SETTINGS_INFO = "Упс, кажется, эта опция еще недоступна"

    def __init__(self):
        pass
