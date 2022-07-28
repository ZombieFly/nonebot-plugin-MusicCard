from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here
    INGORE_ACTIONFAILED: bool = True

    class Config:
        extra = "ignore"
