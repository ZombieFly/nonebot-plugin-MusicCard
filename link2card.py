import contextlib
from typing import Union
import httpx
from json import loads
from re import search


from nonebot.adapters.onebot.v11 import MessageSegment

from .exceptions import NextMusicPlatform
from .data import MusicPlatform


class Model:
    # 构造模型

    def __init__(self, query: dict, mp: MusicPlatform, path: str = str()) -> None:
        self.query = query
        self.mp = mp
        if path:
            self.path = path

    async def common(self) -> MessageSegment:
        """通用解析模型"""
        return MessageSegment.music(type_=self.mp.type_, id_=int(self.query[self.mp.Sid_key][0]))

    async def SPqq(self) -> MessageSegment:
        """网页版&手机客户端链接解析模型"""
        try:
            split_path = self.path.split('/')
            if (id := split_path[split_path.index('songDetail') + 1]).isnumeric():
                # 纯数字id直接发送卡片
                return MessageSegment.music(type_='qq', id_=int(id))
        except ValueError:
            try:
                pattern = r"window.__ssrFirstPageData__\s*=\s*({.*})<"
                url = f'https://{self.mp.url_feature}{self.path}?__={self.query["__"][0]}'
            except KeyError as e:
                raise NextMusicPlatform(self.mp.name) from e
        else:
            pattern = r"window.__INITIAL_DATA__\s*=\s*({.*})"
            url = f'https://y.qq.com{self.path}'

        async with httpx.AsyncClient() as client:
            r = await client.get(url, follow_redirects=True)
        contx: str = r.text

        if not (match := search(pattern, contx)):
            raise NextMusicPlatform(self.mp.name)
        match = match.group(1)
        try:
            data = loads(match)
            return MessageSegment.music(type_='qq', id_=int(data['songList'][0]['id']))
        except Exception:
            data = loads(match.replace('undefined', '""'))
            return MessageSegment.music(type_='qq', id_=int(data['detail']['id']))

    async def kg(self) -> MessageSegment:
        """酷狗音乐解析模型"""
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


async def handle(path: str, query: dict, mp: MusicPlatform) -> Union[MessageSegment, None]:
    """卡片处理

    Args:
        `path` (str): 解析路径
        `query` (dict): 解析后参数
        `mp` (MusicPlatform): 音乐平台

    Returns:
        - 音乐卡片 `MessageSegment`
        - 无法生成卡片时返回 `None`
    """
    with contextlib.suppress(NextMusicPlatform, ):
        if (path in mp.path) and (mp.Sid_key in query):
            model = Model(query, mp)
            return await getattr(model, mp.model)()

        elif not mp.Sid_key:
            model = Model(query, mp, path)
            return await getattr(model, mp.model)()
