class StreamInfo:
    url: str
    resolution: str
    bandwidth: int
    frame_rate: float
    codecs: str
    uid: str
    nickname: str

    def __init__(
        self,
        url: str,
        resolution: str,
        bandwidth: int,
        frame_rate: float,
        codecs: str,
        uid: str = "",
        nickname: str = "",
    ):
        self.url = url
        self.uid = uid
        self.nickname = nickname
        self.resolution = resolution
        self.bandwidth = bandwidth
        self.frame_rate = frame_rate
        self.codecs = codecs

    def __str__(self) -> str:
        return f"StreamInfo(uid={self.uid}, nickname={self.nickname}, resolution={self.resolution}, bandwidth={self.bandwidth}, frame_rate={self.frame_rate}, codecs={self.codecs})"

    def __repr__(self) -> str:
        return self.__str__()
