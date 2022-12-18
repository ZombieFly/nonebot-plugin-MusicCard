class ConstructCardException(Exception):
    """构造音乐卡片异常基类"""

    def __init__(self, error):
        self.error = error

    def __unicode__(self):
        return "构造音乐卡片时发生异常：\"{0}\"".format(self.error)


class NextMusicPlatform(ConstructCardException):
    """下一个音乐平台"""

    def __init__(self, mp_name):
        self.mp_name = mp_name

    def __unicode__(self):
        return f"该链接不是{self.mp_name}的一条音乐分享路径，正在尝试下一个音乐平台"


class NoSongId(ConstructCardException):
    """无歌曲id"""

    def __init__(self):
        pass

    def __unicode__(self):
        return "链接内缺少歌曲id"


class NotSongShare(ConstructCardException):
    """不是分享链接"""

    def __init__(self, mp_name, mp_path):
        self.mp_name = mp_name
        self.mp_path = mp_path

    def __unicode__(self):
        return f'该链接不是{self.mp_name}的一条音乐分享路径，正确的路径应是"{self.mp_path}"'


class GetSPqqIDError(ConstructCardException):
    """获取SPqq音乐id时发生异常"""

    def __init__(self):
        pass

    def __unicode__(self):
        return "获取SPqq音乐id时发生异常"
