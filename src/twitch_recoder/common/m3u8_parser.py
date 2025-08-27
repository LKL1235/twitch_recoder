from loguru import logger
from twitch_recoder.common.utils import format_bandwidth
from twitch_recoder.types.typeinfo import StreamInfo


def parse_m3u8_url(m3u8_url: str) -> list[StreamInfo]:
    """
    解析M3U8播放列表,提取不同分辨率的流媒体URL

    Args:
        m3u8_url (str): M3U8播放列表内容

    Returns:
        list[StreamInfo]: 包含流媒体信息的StreamInfo对象列表
    """
    streams = []
    lines = m3u8_url.split("\n")

    for index, line in enumerate(lines):
        line = line.strip()
        if line.startswith("#EXT-X-STREAM-INF"):
            # 解析流媒体信息
            bandwidth = None
            resolution = None
            frame_rate = None
            codecs = None
            url = None

            # 提取BANDWIDTH, RESOLUTION, FRAME-RATE等信息
            if "BANDWIDTH=" in line:
                bandwidth = int(line.split("BANDWIDTH=")[1].split(",")[0])

            if "RESOLUTION=" in line:
                resolution = line.split("RESOLUTION=")[1].split(",")[0]

            if "FRAME-RATE=" in line:
                frame_rate = float(line.split("FRAME-RATE=")[1].split(",")[0])

            if "CODECS=" in line:
                codecs = line.split('CODECS="')[1].split('"')[0]

            # 查找下一个HTTPS行（流媒体URL）
            for next_index in range(index + 1, len(lines)):
                next_line = lines[next_index].strip()
                if next_line.startswith("https://"):
                    url = next_line
                    break

            if url:
                # 创建StreamInfo对象
                stream_info = StreamInfo(
                    url=url,
                    resolution=resolution or "未知",
                    bandwidth=bandwidth or 0,
                    frame_rate=frame_rate or 0.0,
                    codecs=codecs or "未知",
                )
                streams.append(stream_info)
                logger.debug(f"找到流媒体: {stream_info}")

    return streams

