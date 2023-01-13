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


MPList: list[MusicPlatform] = [

    MusicPlatform(
        name='网易云音乐',
        url_feature='music.163.com',
        model='common',

        path=['/song', '/m/song', "/#/song"],
        type_='163',
        Sid_key='id'
    ),

    MusicPlatform(
        name='QQ音乐1',
        url_feature='c.y.qq.com',
        model='SPqq',

        path=['/base/fcgi-bin/u'],
        type_='qq',
        Sid_key=''

    ),

    MusicPlatform(
        name='QQ音乐2',
        url_feature='i.y.qq.com',
        model='common',

        path=['/v8/playsong.html'],
        type_='qq',
        Sid_key='songid'

    ),

    MusicPlatform(
        name='QQ音乐3',
        url_feature='y.qq.com',
        model='SPqq',

        path=['/n/ryqq/songDetail'],
        type_='qq',
        Sid_key=''

    ),

]

"""     kg := (MusicPlatform(
        name='酷狗音乐',
        url_feature='kugou.com',
        model='kg',

        path=['/song'],
        type_=str(),
        Sid_key='hash'

    ),) """
