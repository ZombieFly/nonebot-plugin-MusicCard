import re
from urllib.parse import ParseResult, urlparse, parse_qs

from nonebot import get_driver, on_keyword
from nonebot.log import logger
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed
from nonebot.adapters.onebot.v11 import MessageSegment

from . import link2card, data
from .exceptions import ConstructCardException

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

keys = []
for mps in data.MPList:
    keys.extend(mps.url_feature)


KEYWORDS: set = set(keys)

INGORE_ACTIONFAILED: bool = config.INGORE_ACTIONFAILED

card = on_keyword(KEYWORDS)


def get_urls(raw: str) -> list[str]:
    """获取文本中所有的链接

    Args:
        - raw (str): 原始文本

    Returns:
        - list[str]: 链接
    """
    return re.findall(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        raw,
    )


def urls_to_parse(urls: list[str]) -> list[tuple[str, ParseResult]]:
    """将链接转换为解析结果

    Args:
        - urls (list[str]): 链接

    Returns:
        - list[tuple[str, ParseResult]]: 解析结果
    """
    return [(url, urlparse(url, allow_fragments=False)) for url in urls]


@ card.handle()
async def _(event: MessageEvent):

    # 已经发送过的卡片缓存
    msCahce: list[MessageSegment] = []

    logger.debug('触发Nonebot-plgin-MusicCard')
    urls = get_urls(event.message.extract_plain_text())
    for url, parse_result in urls_to_parse(urls):

        url_netloc = parse_result.netloc

        for mp in data.MPList:

            if mp.url_feature in url_netloc:
                qs = parse_qs(parse_result.query)
                logger.debug(
                    f'为链接 {url} 找到对应mp<{mp.name}>，解析路径为:{str(parse_result.path)}，参数为{str(qs)}')

                if out := await link2card.handle(parse_result.path, qs, mp):
                    await send_out(msCahce, out)


async def send_out(msCahce: list[MessageSegment], out: MessageSegment):
    """发送卡片，并去重

    Args:
        - msCahce (list[MessageSegment]): 已发送的卡片缓存
        - out (MessageSegment): 卡片

    Raises:
        - err: 配置中设置不忽略 `ActionFailed` 报错时，抛出 `ActionFailed` 异常
    """
    if (out not in msCahce):
        try:
            msCahce.append(out)
            return await card.send(out)

        except ConstructCardException:
            pass
        except ActionFailed as err:
            # * 忽略ActionFailed报错（可能是由于链接中的id不存在对应的音乐）
            if not INGORE_ACTIONFAILED:
                raise err
    else:
        logger.debug('重复卡片，已忽略')
