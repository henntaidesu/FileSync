import os
import time
import shutil
import json
import sys
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 读取配置文件
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# 获取监控的文件夹路径和同步到的文件夹路径
src_folder = config[0].get("OldFilePath")
dest_folder = config[0].get("NewFilePath")
log_level = config[1].get("log_level")

# 创建日志记录器
logger = logging.getLogger()
logger.setLevel(logging.getLevelName(log_level))

# 配置日志记录器，同时输出到控制台和日志文件
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("INFO.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()  # 添加控制台处理程序
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def err_log(error_message):
    # 记录错误日志
    logger.error(error_message)


def info_log(info_message):
    # 记录信息日志
    logger.info(info_message)


class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        try:
            if event.is_directory:
                # 获取新创建文件夹的路径
                new_folder = event.src_path

                # 构建目标文件夹路径，保持相同的文件结构
                dest_folder_path = new_folder.replace(src_folder, dest_folder, 1)

                # 创建目标文件夹
                os.makedirs(dest_folder_path, exist_ok=True)

                info_log(f"Now Sync Directory：{new_folder}")
            else:
                # 获取新创建文件的路径
                src_path = event.src_path

                # 构建目标路径，保持相同的文件结构
                dest_path = src_path.replace(src_folder, dest_folder, 1)

                # 检查目标文件是否已经存在
                if os.path.exists(dest_path):
                    # 获取源文件和目标文件的修改时间
                    src_mtime = os.path.getmtime(src_path)
                    dest_mtime = os.path.getmtime(dest_path)

                    # 如果修改时间不一样，则进行同步
                    if src_mtime != dest_mtime:
                        shutil.copy2(src_path, dest_path)
                        info_log(f"Now Sync File：{src_path}")
                    else:
                        info_log(f"File already exists and has the same modification time, skipping: {src_path}")
                else:
                    # 文件不存在，直接进行同步
                    shutil.copy2(src_path, dest_path)
                    info_log(f"Now Sync File：{src_path}")
        except Exception as e:
            error_message = f"错误信息: {str(e)}\n错误类型: {type(e).__name__}"
            error_message += f"\n发生错误的位置: {sys.exc_info()[2].tb_frame.f_code.co_filename} 第 {sys.exc_info()[2].tb_lineno} 行"
            err_log(error_message)


if __name__ == "__main__":
    try:
        # 创建监控器
        event_handler = MyHandler()
        observer = Observer()

        # 添加监控路径
        observer.schedule(event_handler, path=src_folder, recursive=True)  # 设置 recursive=True 以监控子文件夹

        # 启动监控
        observer.start()
        print(f"Now Monitor Directory：{src_folder}")

        while True:
            time.sleep(1)  # 持续监视，无需退出

    except Exception as e:
        error_message = f"错误信息: {str(e)}\n错误类型: {type(e).__name__}"
        error_message += f"\n发生错误的位置: {sys.exc_info()[2].tb_frame.f_code.co_filename} 第 {sys.exc_info()[2].tb_lineno} 行"
        err_log(error_message)
