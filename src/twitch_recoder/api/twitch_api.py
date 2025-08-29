import requests
from loguru import logger
from twitch_recoder.config.my_config import (
    AUTHED_HEADERS,
    TWITCH_GQL_URL,
    DEFAULT_HEADERS,
    PLAYBACK_ACCESS_TOKEN_QUERY,
    DEFAULT_VARIABLES,
)
from twitch_recoder.common.m3u8_parser import parse_m3u8_url
from twitch_recoder.common.stream_sorter import get_best_stream
from twitch_recoder.common.utils import get_proxies
from twitch_recoder.types.errors import NetWorkErr, OfflineErr
from twitch_recoder.types.typeinfo import StreamInfo


def get_token_and_sign(uid: str):
    """
    获取Twitch流媒体的访问令牌和签名

    Args:
        uid (str): Twitch频道用户名

    Returns:
        tuple: (token, sign)
    """
    url = TWITCH_GQL_URL

    headers = DEFAULT_HEADERS.copy()

    data = {
        "operationName": "PlaybackAccessToken_Template",
        "query": PLAYBACK_ACCESS_TOKEN_QUERY,
        "variables": {
            **DEFAULT_VARIABLES,
            "login": uid,
        },
    }

    try:
        logger.debug(f"正在获取 {uid} 的访问令牌...")
        proxies = get_proxies()
        response = requests.post(url, headers=headers, json=data, timeout=10, proxies=proxies)

        if response.status_code == 200:
            response_data = response.json()
            token = response_data["data"]["streamPlaybackAccessToken"]["value"]
            sign = response_data["data"]["streamPlaybackAccessToken"]["signature"]
            logger.debug(f"成功获取令牌: token={token[:50]}..., sign={sign}")
            return token, sign
        else:
            logger.error(f"获取uid:{uid}, url:{url}令牌失败: {response.status_code}")
            logger.debug(f"response: {response.text}")
            logger.debug(f"headers: {response.request.headers}")
            logger.debug(f"data: {response.request.body}")
            return None, None

    except Exception as e:
        logger.error(f"获取令牌异常: {e}")
        return None, None


def get_m3u8_url(uid: str, token: str, sign: str):
    """
    获取M3U8播放列表URL

    Args:
        uid (str): Twitch频道用户名
        token (str): 访问令牌
        sign (str): 签名

    Returns:
        str: M3U8播放列表内容
    """
    from twitch_recoder.config.my_config import TWITCH_USHER_URL, DEFAULT_PARAMS, DEFAULT_USER_AGENT

    url = TWITCH_USHER_URL.format(uid=uid)
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/x-mpegURL, application/vnd.apple.mpegurl, application/json, text/plain",
        "Referer": "https://www.twitch.tv/",
    }
    params = {
        **DEFAULT_PARAMS,
        "sig": sign,
        "token": token,
    }

    proxies = get_proxies()
    response = requests.get(url, headers=headers, params=params, timeout=10, proxies=proxies)
    logger.debug(
        f"uid:{uid}, url:{url}, status_code: {response.status_code}, headers: {response.request.headers}, params: {response.request.body}"
    )
    result = response.text
    return result


def get_room_info(uid: str, token: str):
    url = TWITCH_GQL_URL
    headers = AUTHED_HEADERS.copy()
    headers["Client-Integrity"] = token
    data = [
        {
            "operationName": "ChannelShell",
            "variables": {"login": uid},
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "580ab410bcd0c1ad194224957ae2241e5d252b2c5173d8e0cce9d32d5bb14efe",
                }
            },
        },
    ]

    proxies = get_proxies()
    response = requests.post(url, headers=headers, json=data, timeout=10, proxies=proxies)
    if response.status_code != 200:
        logger.error(f"获取uid:{uid}, url:{url}房间信息失败: {response.status_code}")
        logger.debug(f"response: {response.text}")
        logger.debug(f"headers: {response.request.headers}")
        logger.debug(f"data: {response.request.body}")
        return None, False

    json_data = response.json()
    user_data = json_data[0]['data']['userOrError']
    login_name = str(user_data["login"]) if user_data["login"] else ""
    display_name = str(user_data['displayName']) if user_data['displayName'] else login_name
    nickname = f"{display_name}-{login_name}"
    status = True if user_data['stream'] else False
    return nickname, status


def process_twitch_stream(uid: str) -> StreamInfo | None:
    """处理Twitch流媒体的核心逻辑"""

    # 获取访问令牌
    token, sign = get_token_and_sign(uid)

    if token and sign:
        nickname, status = get_room_info(uid, token)
        if not status:
            raise OfflineErr(f"频道 {uid} 未开播")

        # 获取M3U8播放列表
        result = get_m3u8_url(uid, token, sign)
        logger.debug(f"uid:{uid}获取到M3U8播放列表长度: {len(result)}")

        # 解析播放列表
        streams = parse_m3u8_url(result)
        logger.debug(f"uid:{uid}解析到 {len(streams)} 个流媒体源")

        for stream in streams:
            stream.uid = uid
            if nickname:
                stream.nickname = nickname
            else:
                stream.nickname = uid

        # 获取最佳流媒体
        best_stream = get_best_stream(streams)
        return best_stream
    else:
        raise NetWorkErr("无法获取访问令牌，请检查网络连接或认证信息")
