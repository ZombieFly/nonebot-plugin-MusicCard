from typing import Literal, Callable
from pydantic import BaseModel
from typing import Union
from json import loads
from re import search
import contextlib
import httpx


from nonebot.adapters.onebot.v11 import MessageSegment


from .exceptions import NextMusicPlatform
from .data import MusicPlatform


QLinkSource = Literal['web', 'client']


class QLinkActionAttrs(BaseModel):
    """qq音乐分享链接解析过程参数

    - source (QLinkSource): 链接来源
    - pattern (str): 正则表达式
    - url (str): 请求链接

    """

    source: QLinkSource
    pattern: str
    url: str

    get_data: Callable
    get_Sid: Callable


class Model:
    # 构造模型

    def __init__(self, query: dict, mp: MusicPlatform, path: str = str()) -> None:
        self.query = query
        self.mp = mp

        if path:
            self.path = path

    def _set_actions(self, source_opt: QLinkSource) -> None:
        """设置解析过程参数

        Args:
            source_opt (QLinkSource): 链接来源
        """
        self.QLinkActionAttrs = (QLinkActionAttrs(
            source='web',
            pattern=r"window.__INITIAL_DATA__\s*=\s*({.*})",
            url=f'https://y.qq.com{self.path}',
            get_data=lambda match: loads(
                    match.group(1).replace('undefined', '""')),
            get_Sid=lambda data: int(
                data['detail']['id']),
        )

            if source_opt == 'web' else

            QLinkActionAttrs(
                source='client',
                pattern=r"window.__ssrFirstPageData__\s*=\s*({.*})<",
                url=f'https://{self.mp.url_feature}{self.path}?__={self.query["__"][0]}',
                get_data=lambda match: loads(
                    match.group(1)),
                get_Sid=lambda data: int(
                    data['songList'][0]['id']),
        ))

    async def common(self) -> MessageSegment:
        """通用解析模型"""
        return MessageSegment.music(type_=self.mp.type_, id_=int(self.query[self.mp.Sid_key][0]))

    async def SPqq(self) -> MessageSegment:
        """qq网页版&手机客户端链接解析模型"""
        try:
            split_path = self.path.split('/')
            if (id := split_path[split_path.index('songDetail') + 1]).isnumeric():
                # 纯数字id直接发送卡片
                return MessageSegment.music(type_='qq', id_=int(id))
        except ValueError:
            try:
                self._set_actions('client')
            except KeyError as e:
                raise NextMusicPlatform(self.mp.name) from e
        else:
            self._set_actions('web')

        # 网页请求
        async with httpx.AsyncClient() as client:
            r = await client.get(self.QLinkActionAttrs.url, follow_redirects=True)
        contx: str = r.text

        if not (match := search(self.QLinkActionAttrs.pattern, contx)):
            raise NextMusicPlatform(self.mp.name)

        data = self.QLinkActionAttrs.get_data(match)
        Sid = self.QLinkActionAttrs.get_Sid(data)

        return MessageSegment.music(type_='qq', id_=Sid)

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
