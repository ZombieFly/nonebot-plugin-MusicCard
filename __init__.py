import re
from urllib.parse import urlparse, parse_qs

from nonebot import get_driver, on_keyword
from nonebot.adapters.onebot.v11.event import MessageEvent

from . import link2card

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

KEYWORDS_MAP = config.KEYWORDS_MAP
KEYWORDS = set(KEYWORDS_MAP.keys())

card = on_keyword(KEYWORDS)


def get_url(raw: str) -> list:
    url = re.findall(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', raw)
    return url


@card.handle()
async def _(event: MessageEvent):

    urls = get_url(event.message.extract_plain_text())
    for url in urls:
        parse_result = urlparse(url)

        url_netloc = parse_result.netloc

        for url in KEYWORDS:

            if url in url_netloc:
                out = getattr(link2card, KEYWORDS_MAP[url])(
                    parse_result.path, parse_qs(parse_result.query))

                if out:
                    await card.send(out)
