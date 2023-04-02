from random import choice

from app.contest.models import Member

COMMAND_START_KEYBOARD = {
    "one_time": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "label": "Активировать бота",
                    "payload": {"button": "start"},
                }
            }
        ]
    ],
}

START_CONTEST_KEYBOARD = {
    "one_time": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "label": "Запустить конкурс",
                    "payload": {"button": "starting"},
                },
                "color": "positive",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Доступные команды",
                    "payload": {"button": "help"},
                },
                "color": "primary",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Правила конкурса",
                    "payload": {"button": "rules"},
                },
                "color": "secondary",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Победитель прошлой игры",
                    "payload": {"button": "history"},
                },
                "color": "primary",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Статистика",
                    "payload": {"button": "statistic"},
                },
                "color": "secondary",
            }
        ],
        # [
        #     {
        #         "action": {
        #             "type": "text",
        #             "label": "Settings",
        #             "payload": {"button": "settings"},
        #         },
        #     }
    ],
}

SETTINGS_KEYBOARD = {
    "one_time": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "label": "Время раунда",
                    "payload": {"button": "time"},
                }
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Схема",
                    "payload": {"button": "schema"},
                },
            }
        ],
    ],
}

CONTEST_KEYBOARD = {
    "one_time": False,
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "label": "Активные участники",
                    "payload": {"button": "score"},
                },
                "color": "primary",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Долго не отвечаю? Тык сюда!",
                    "payload": {"button": "starting"},
                },
                "color": "secondary",
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "Закончить конкурс",
                    "payload": {"button": "stop"},
                },
                "color": "negative",
            }
        ],
    ],
}


def set_inline_keyboard(left: Member, right: Member) -> dict:
    keyboard = {
        "inline": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": f"{left.name}",
                        "payload": {"button": f"{left.id}"},
                    },
                    "color": "secondary",
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": f"{right.name}",
                        "payload": {"button": f"{right.id}"},
                    },
                    "color": "primary",
                }
            ],
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Пусть решит случай",
                        "payload": {"button": f"{choice((right.id, left.id))}"},
                    },
                    "color": "positive",
                }
            ],
        ],
    }
    return keyboard
