import re
from urllib.parse import urlparse, parse_qs

from nonebot import get_driver, on_keyword
from nonebot.log import logger
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed

from . import link2card, data

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

KEYWORDS: set = {mp.url_feature for mp in data.MPList}

INGORE_ACTIONFAILED: bool = config.INGORE_ACTIONFAILED

card = on_keyword(KEYWORDS)


def get_url(raw: str) -> list:
    return re.findall(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        raw.replace(r'/#', '?'),
    )


@card.handle()
async def _(event: MessageEvent):
    logger.debug('触发Nonebot-plgin-MusicCard')
    urls = get_url(event.message.extract_plain_text())
    for url in urls:
        parse_result = urlparse(url)

        url_netloc = parse_result.netloc

        for mp in data.MPList:

            if mp.url_feature in url_netloc:
                qs = parse_qs(parse_result.query)
                logger.debug(
                    f'找到对应mp<{mp.name}>，解析路径为{str(parse_result.path)}，参数为{str(qs)}')

                out = await link2card.handle(parse_result.path, qs, mp)

                if out:
                    try:
                        await card.send(out)

                    except ActionFailed as err:
                        # * 忽略ActionFailed报错（可能是由于链接中的id不存在对应的音乐）
                        if not INGORE_ACTIONFAILED:
                            raise err
