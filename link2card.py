from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment

from .exceptions import NotSongShare, NoSongId
from .data import MusicPlatform


class Model:
    # 构造模型

    def __init__(self, query: dict, mp: MusicPlatform) -> None:
        self.query = query
        self.mp = mp

    def common(self) -> MessageSegment:
        return MessageSegment.music(type_=self.mp.type_, id_=int(self.query[self.mp.Sid_key][0]))


def handle(path: str, query: dict, mp: MusicPlatform) -> Union[MessageSegment, str, None]:

    try:
        if (path in mp.path) and (mp.Sid_key in query):
            model = Model(query, mp)
            return getattr(model, mp.model)()

        elif path not in mp.path:
            raise NotSongShare(mp.name, '、'.join(mp.path))

        elif mp.Sid_key not in query:
            raise NoSongId

    except (NotSongShare, NoSongId):
        pass

    except Exception as err:
        return repr(err)
