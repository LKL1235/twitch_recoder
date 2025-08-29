import subprocess
import time
from loguru import logger


def recode(url: str, proxy: str = "", save_file_path: str = "", nick_name: str = "", max_time_limit: int = 3600):
    """
    录制Twitch流媒体

    Args:
        url (str): 流媒体URL
        proxy (str): 代理设置
        save_file_path (str): 保存文件路径
        nick_name (str): 昵称

    Returns:
        bool: 录制是否成功
    """
    try:
        user_agent = (
            "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 ("
            "KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile "
            "Safari/537.36"
        )

        rw_timeout = "50000000"
        analyzeduration = "40000000"
        probesize = "20000000"
        bufsize = "15000k"
        max_muxing_queue_size = "2048"

        # fmt: off
        ffmpeg_command = [
            'ffmpeg', "-y",
            # "-v", "verbose",
            "-rw_timeout", rw_timeout,
            # "-loglevel", "error",
            "-hide_banner",
            "-user_agent", user_agent,
            "-protocol_whitelist", "rtmp,crypto,file,http,https,tcp,tls,udp,rtp,httpproxy",
            "-thread_queue_size", "1024",
            "-analyzeduration", analyzeduration,
            "-probesize", probesize,
            "-fflags", "+discardcorrupt+genpts", # 添加genpts处理时间戳问题
            "-re", "-i", url,
            "-timeout", "10000000",              # 10秒连接超时
            "-bufsize", bufsize,
            "-sn", "-dn",
            "-reconnect_delay_max", "15",      # 最大重连延迟减少到15秒
            "-reconnect_streamed", "-reconnect_at_eof",
            "-reconnect", "1",                  # 启用自动重连
            "-reconnect_on_network_error", "1", # 网络错误时重连
            "-reconnect_on_http_error", "1",    # HTTP错误时重连
            "-max_muxing_queue_size", max_muxing_queue_size,
            "-correct_ts_overflow", "1",
            "-avoid_negative_ts", "1",
            "-map", "0",
            "-c:v", "copy",
            "-c:a", "copy",
        ]
        if proxy:
            ffmpeg_command.extend(["-http_proxy", proxy])

        if max_time_limit and max_time_limit >= 0:
            ffmpeg_command.extend(["-t", str(max_time_limit)])

        if not save_file_path:
            if nick_name:
                save_file_path = f"./{nick_name}.mp4"
            else:
                save_file_path = "./twitch_stream.mp4"

        ffmpeg_command.extend(["-f", "mp4", save_file_path])

        # 输出命令行参数
        str_command = [str(item) for item in ffmpeg_command]
        logger.debug(f"执行命令: {' '.join(str_command)}")

        # fmt: on

        # 录制状态控制
        recording_active = True
    except Exception as e:
        logger.error(f"录制过程中发生错误: {e}")
        return False

    try:
        process = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        logger.info(f"开始录制流媒体到: {save_file_path}")
        logger.info(f"FFmpeg进程ID: {process.pid}")

        # 实时输出日志
        while process.poll() is None and recording_active:
            try:
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        line = line.strip()
                        if line:
                            logger.debug(line)
            except Exception as e:
                logger.error(f"读取FFmpeg输出时出错: {e}")
                break

        # 检查录制结果
        if not recording_active:
            logger.info("录制被中断")
            return False
        elif process.returncode == 0:
            logger.info(f"流媒体录制成功,保存路径: {save_file_path}")
            return True
        else:
            logger.error(f"流媒体录制失败 f{save_file_path},错误码: {process.returncode}")
            return False

    except Exception as e:
        # 打印错误堆栈
        import traceback

        traceback.print_exc()
        logger.error(f"录制过程中发生错误: {e}")
        if "process" in locals() and process.poll() is None:
            process.kill()
        return False
    finally:
        # 确保进程被终止
        if "process" in locals() and process.poll() is None:
            try:
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
            except Exception:
                pass
