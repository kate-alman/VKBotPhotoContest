from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class UpdateObject:
    id: int
    peer_id: int
    user_id: int
    body: str


@dataclass
class Update:
    type: str
    object: UpdateObject

    @staticmethod
    def from_dict(update):
        return Update(
            type=update["type"],
            object=UpdateObject(
                update["object"]["id"],
                update["object"]["peer_id"],
                update["object"]["user_id"],
                update["object"]["body"],
            ),
        )


@dataclass
class Message:
    receiver_id: int
    text: Optional[str] = None
    attachment: Optional[str] = None
    keyboard: Optional[Dict[str, object]] = None

    @staticmethod
    def from_dict(message):
        return Message(
            receiver_id=message["receiver_id"],
            text=message["text"],
            attachment=message["attachment"],
            keyboard=message["keyboard"],
        )
