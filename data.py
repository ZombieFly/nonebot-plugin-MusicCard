from pydantic import BaseModel


class MusicPlatform(BaseModel):
    """MusicPlatform类

    name(str) 平台名
    url_feature(str) url内特征段落
    model(str) 解析模块

    path(list) url路径
    type_(str) 163、qq等的内置类型
    Sid_key(str) url参数内存放id的键名
    """
    name: str
    url_feature: str
    model: str

    path: list
    type_: str
    Sid_key: str


MPList = [

    ne := MusicPlatform(
        name='网易云音乐',
        url_feature='music.163.com',
        model='common',

        path=['/song', '/m/song'],
        type_='163',
        Sid_key='id'
    ),

    qq := MusicPlatform(
        name='QQ音乐',
        url_feature='y.qq.com',
        model='common',

        path=['/v8/playsong.html'],
        type_='qq',
        Sid_key='songid'

    )
]
