import re
from asyncio.log import logger
import json
import os
import random
import shutil
from time import sleep
import time
import traceback
from bs4 import BeautifulSoup
from typing import Any
import requests
import urllib.request
from pathlib import Path
from .txt2img import Txt2Img
from nonebot.params import ArgPlainText
from nonebot.rule import to_me
from nonebot import (
    on_command,
    on_keyword,
    on_notice,
    on_message,
    on_request,
    get_bots
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageSegment,
    MessageEvent,
    Message,
    PokeNotifyEvent,
    GroupRequestEvent,
    GroupIncreaseNoticeEvent,
    PrivateMessageEvent
)
from .utils import *


PATH_RESOURCES = Path.cwd() / "resources"  # 资源目录
PATH_DATA = Path.cwd() / "data"  # 数据目录
PATH_IMAGES = PATH_RESOURCES / "image"  # 保存的image图片目录
PATH_SOMEIMAGES = PATH_RESOURCES / "someImage"  # 保存的someImage图片目录
FILE_INTERACTION = PATH_RESOURCES / "interaction.json"  # interaction.json目录
FILE_ADMINS = PATH_RESOURCES / "admins.json"  # admins.json目录
FILE_SOMEIMAGE = PATH_RESOURCES / "someImage.json"  # someImage.json目录
FILE_KEYWORD = PATH_RESOURCES / "key-word.json"  # key-word.json目录
FILE_WHITE = PATH_RESOURCES / "white.json"  # white.json目录
FILE_AUTOREPLY = PATH_RESOURCES / "autoReply.json"  # autoReply.json目录
FILE_REJRCT_GROUP_REQUEST = PATH_RESOURCES / \
    'rejectGroupRequest.json'    # reject.json目录
FILE_TODAY_RANK = PATH_DATA / "today_rank.json"    # 今日题数json目录
FILE_GOODMORNING = PATH_DATA / "goodmorning.json"  # 早安json
FILE_MESSAGE = PATH_DATA / "message.json"  # 消息json

PATH_TXT2IMG = PATH_DATA / "TXT2IMG"  # TXT2IMG目录
PATH_SOMEIMAGE = PATH_TXT2IMG / "someImage"  # 生成的someImage图片目录
PATH_INTERACTION = PATH_TXT2IMG / "interaction"  # 生成的interaction图片目录
IMAGE_INTERACTION = PATH_INTERACTION / "interaction.png"  # 生成的interaction.png
IMAGE_SOMEIMAGE = PATH_SOMEIMAGE / "someImage.png"  # 生成的someImage.png

SUPERUSER = "2737664805"  # 超管
dict_msg_id = {}
list_msg_id_and_user_id = []
time_image = 0
time_rank = 0
rank_max_length = 20
isGetTodayRank = False
isRefreshing = False

# 对json文件进行下载
with open(FILE_INTERACTION, 'r', encoding='utf-8') as file_interaction:
    data_interaction = json.load(file_interaction)
with open(FILE_ADMINS, 'r', encoding='utf-8') as file_admins:
    data_admins = json.load(file_admins)
with open(FILE_SOMEIMAGE, 'r', encoding='utf-8') as file_someImage:
    data_someImage = json.load(file_someImage)
with open(FILE_KEYWORD, 'r', encoding='utf-8') as file_keyword:
    data_keyword = json.load(file_keyword)
with open(FILE_WHITE, 'r', encoding='utf-8') as file_white:
    data_white = json.load(file_white)
with open(FILE_AUTOREPLY, 'r', encoding='utf-8') as file_autoReply:
    data_autoReply = json.load(file_autoReply)
with open(FILE_REJRCT_GROUP_REQUEST, 'r') as file_reject_group_request:
    data_reject_group_request = json.load(file_reject_group_request)
with open(FILE_TODAY_RANK, 'r', encoding='utf-8') as file_today_rank:
    data_today_rank = json.load(file_today_rank)
with open(FILE_GOODMORNING, 'r') as file_goodmorning:
    data_goodmoring = json.load(file_goodmorning)
with open(FILE_MESSAGE, 'r', encoding='utf-8') as file_message:
    data_message = json.load(file_message)


# 正则匹配str1和str2
class regex2:
    def __init__(self, text):
        str = re.findall("\\*(.*)\\*(.*)\\*", text, re.S)
        self.str1 = "".join(str[0][0])
        self.str2 = "".join(str[0][1])


# rule:检查是否为超管
def check_SuperUser(event) -> bool:
    return event.get_user_id() == SUPERUSER


# rule=检查是否为管理员
async def check_Admin(bot: Bot, event) -> bool:
    if event.message_type == 'group':
        info = await bot.get_group_member_info(
            group_id=event.group_id, user_id=event.user_id)
        for id in data_admins:
            if str(id) == str(event.user_id) or info['role'] == 'admin':
                return True
    else:
        for id in data_admins:
            if str(id) == str(event.user_id):
                return True
    return False


# rule=检查是否在白名单中
def check_White(event: GroupMessageEvent) -> bool:
    for id in data_white:
        if str(id) == str(event.user_id):
            return True
    return False


# 检查是否为响应群聊
def check_group(event: GroupMessageEvent) -> bool:
    dict_group = {'班级群': 330730920, '21新生群': 967658105,
                  '闲聊群': 770690237, '23': 839652032}
    for ele in dict_group:
        if dict_group[ele] == event.group_id:
            return True
    return False
