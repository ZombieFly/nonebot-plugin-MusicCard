from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here
    KEYWORDS_MAP: dict[str, str] = {'music.163.com': 'ne'}
    INGORE_ACTIONFAILED: bool = True

    class Config:
        extra = "ignore"
