from loguru import logger
from twitch_recoder.common.utils import extract_resolution_width
from twitch_recoder.types.typeinfo import StreamInfo


def sort_streams(streams: list[StreamInfo]):
    """
    排序流媒体：
    1. 先按分辨率从大到小排序
    2. 相同分辨率再按帧率从大到小排序
    3. 如果缺少分辨率或帧率信息，则按带宽从大到小排序
    """

    def can_sort_by_resolution_and_framerate(streams):
        """检查是否所有流媒体都有分辨率和帧率信息"""
        for stream in streams:
            if not stream.resolution or not stream.frame_rate:
                return False
        return True

    # 检查是否所有流媒体都有分辨率和帧率信息
    if can_sort_by_resolution_and_framerate(streams):
        # 按分辨率和帧率排序
        return sorted(
            streams,
            key=lambda x: (
                extract_resolution_width(x.resolution),
                x.frame_rate,
            ),
            reverse=True,
        )
    else:
        # 按带宽排序
        logger.debug("部分流媒体缺少分辨率或帧率信息，按带宽排序")
        return sorted(streams, key=lambda x: x.bandwidth, reverse=True)


def get_best_stream(streams: list[StreamInfo]):
    """
    获取最佳质量的流媒体

    Args:
        streams (list[StreamInfo]): 流媒体StreamInfo对象列表

    Returns:
        StreamInfo: 最佳质量的流媒体信息，如果没有则返回None
    """
    if not streams:
        return None

    sorted_streams = sort_streams(streams)
    best_stream = sorted_streams[0]

    logger.debug(
        f"{best_stream.uid}选择最佳流媒体: 分辨率: {best_stream.resolution}, 带宽: {best_stream.bandwidth} bps, 帧率: {best_stream.frame_rate} fps, 编码: {best_stream.codecs}"
    )

    return best_stream
