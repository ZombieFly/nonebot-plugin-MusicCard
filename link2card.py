from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment

from .exceptions import NotSongShare, NoSongId


def ne(path: str, query: dict) -> Union[MessageSegment, str, None]:

    mp_path = '/song'
    try:
        if (path == mp_path) and ('id' in query):
            return MessageSegment.music(type_='163', id_=int(query['id'][0]))

        elif path != mp_path:
            raise NotSongShare("网易云", mp_path)

        elif 'id' not in query:
            raise NoSongId

    except (NotSongShare, NoSongId):
        pass

    except Exception as err:
        return repr(err)
