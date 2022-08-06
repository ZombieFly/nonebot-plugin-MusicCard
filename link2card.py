from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment

from .exceptions import NotSongShare, NoSongId
from .data import MusicPlatform


class Model:
    @staticmethod
    def common(query: dict, mp: MusicPlatform):
        return MessageSegment.music(type_=mp.type_, id_=int(query[mp.Sid_key][0]))


def handle(path: str, query: dict, mp: MusicPlatform) -> Union[MessageSegment, str, None]:

    try:
        if (path in mp.path) and (mp.Sid_key in query):
            return getattr(Model, mp.model)(query, mp)

        elif path not in mp.path:
            raise NotSongShare(mp.name, '、'.join(mp.path))

        elif mp.Sid_key not in query:
            raise NoSongId

    except (NotSongShare, NoSongId):
        pass

    except Exception as err:
        return repr(err)
