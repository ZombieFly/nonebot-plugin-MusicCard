from typing import Union
import httpx

from nonebot.adapters.onebot.v11 import MessageSegment

from .exceptions import NotSongShare, NoSongId
from .data import MusicPlatform


class Model:
    # 构造模型

    def __init__(self, query: dict, mp: MusicPlatform) -> None:
        self.query = query
        self.mp = mp

    async def common(self) -> MessageSegment:
        return MessageSegment.music(type_=self.mp.type_, id_=int(self.query[self.mp.Sid_key][0]))

    async def kg(self) -> MessageSegment:
        async with httpx.AsyncClient() as client:
            r = await client.get(f'http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={self.query["hash"][0]}')
        contx: dict = r.json()

        print(
            f"{contx['url']}\n{self.query['hash'][0]}\n{contx['fileName']}\n{contx['album_img'].replace('/{size}', '')}")

        return MessageSegment.music_custom(
            url=f'https://www.kugou.com/song/#hash={self.query["hash"][0]}',
            audio=contx['url'],
            title=contx['fileName'],
            content='',
            img_url=contx['album_img'].replace('/{size}', '')
        )


async def handle(path: str, query: dict, mp: MusicPlatform) -> Union[MessageSegment, str, None]:

    try:
        if (path in mp.path) and (mp.Sid_key in query):
            model = Model(query, mp)
            ret = await getattr(model, mp.model)()
            return ret

        elif path not in mp.path:
            raise NotSongShare(mp.name, '、'.join(mp.path))

        elif mp.Sid_key not in query:
            raise NoSongId

    except (NotSongShare, NoSongId):
        pass

    except Exception as err:
        return repr(err)
