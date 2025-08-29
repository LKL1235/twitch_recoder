"""
Twitch录制器配置模块
"""

# Twitch API配置
import json

from loguru import logger


TWITCH_GQL_URL = "https://gql.twitch.tv/gql"
TWITCH_USHER_URL = "https://usher.ttvnw.net/api/channel/hls/{uid}.m3u8"

# 默认请求头
DEFAULT_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US",
    "client-id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
    "content-type": "text/plain; charset=UTF-8",
    "device-id": "c0434c23cbc5c457",
    "origin": "https://www.twitch.tv",
    "priority": "u=1, i",
    "referer": "https://www.twitch.tv/",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
}

# 默认用户代理
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"

# 默认参数
DEFAULT_PARAMS = {
    "acmb": "eyJBcHBWZXJzaW9uIjoiNmI1NmUyZDAtY2U1Ni00YzQxLTkzNzYtMDhiNGFlYjQ3NjgwIn0%3D",
    "allow_source": "true",
    "browser_family": "microsoft%20edge",
    "browser_version": "139.0",
    "cdm": "wv",
    "fast_bread": "true",
    "include_unavailable": "true",
    "os_name": "Windows",
    "os_version": "NT%2010.0",
    "p": "4830264",
    "platform": "web",
    "play_session_id": "bc0f20cb7106d70c3a9251542f55debc",
    "player_backend": "mediaplayer",
    "player_version": "1.44.0-rc.1.1",
    "playlist_include_framerate": "true",
    "reassignments_supported": "true",
    "supported_codecs": "av1,h264",
    "transcode_mode": "cbr_v1",
}

# GraphQL查询
PLAYBACK_ACCESS_TOKEN_QUERY = """query PlaybackAccessToken_Template($login: String!, $isLive: Boolean!, $vodID: ID!, $isVod: Boolean!, $playerType: String!, $platform: String!) {
    streamPlaybackAccessToken(channelName: $login, params: {platform: $platform, playerBackend: "mediaplayer", playerType: $playerType}) @include(if: $isLive) {
        value
        signature
        authorization {
            isForbidden
            forbiddenReasonCode
        }
        __typename
    }
    videoPlaybackAccessToken(id: $vodID, params: {platform: $platform, playerBackend: "mediaplayer", playerType: $playerType}) @include(if: $isVod) {
        value
        signature
        __typename
    }
}"""

# 默认变量
DEFAULT_VARIABLES = {
    "isLive": True,
    "isVod": False,
    "vodID": "",
    "playerType": "site",
    "platform": "web",
}

AUTHED_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Accept-Language': 'zh-CN',
    'Referer': 'https://www.twitch.tv/',
    'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
    'Client-Integrity': '',
    'Content-Type': 'text/plain;charset=UTF-8',
}

# 默认配置
DEFAULT_CONFIG = {
    "uids": [],
    "data_path": "data",
    "max_time_limit": 3600,
    "proxy": "",
}

class Config:
    def __init__(self, uids: str, data_path: str, max_time_limit: int, proxy: str = ""):
        self.uids = uids
        self.data_path = data_path
        self.max_time_limit = max_time_limit
        self.proxy = proxy

    def reload(self, uids: str, data_path: str, max_time_limit: int, proxy: str = ""):
        self.uids = uids
        self.data_path = data_path
        self.max_time_limit = max_time_limit
        self.proxy = proxy

# 全局配置实例
config: Config = Config(**DEFAULT_CONFIG)


class ConfigReader:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load_config(self):
        global config
        with open(self.config_path, "r") as f:
            try:
                config_dict = json.load(f)
                config.reload(**config_dict)
            except json.decoder.JSONDecodeError:
                logger.error("配置文件格式错误")
                raise ValueError(f"配置文件({self.config_path})格式错误")
            except Exception as e:
                logger.error(f"配置文件读取失败: {e}")
                raise ValueError(f"配置文件({self.config_path})读取失败")
        return True
