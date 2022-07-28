from typing import Union
from nonebot.adapters.onebot.v11 import MessageSegment


def ne(path: str, query: dict) -> Union[MessageSegment, str, None]:
    try:
        if path == '/song':
            return MessageSegment.music(type_='163', id_=int(query['id'][0]))

    except Exception as err:
        return repr(err)
