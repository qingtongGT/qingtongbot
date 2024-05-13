#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

# Custom your logger
#
# from nonebot.log import logger, default_format
# logger.add("error.log",
#            rotation="00:00",
#            diagnose=False,
#            level="ERROR",
#            format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# nonebot.load_builtin_plugins("echo")
# nonebot.load_plugin('nonebot_plugin_gocqhttp')  # 自动连接gocq插件
# nonebot.load_plugin('GenshinUID')
# nonebot.load_plugin("nonebot_plugin_hitokoto")  # 一言
# nonebot.load_plugin("nonebot_plugin_admin")  # 管理插件
# nonebot.load_plugin('nonebot_plugin_minesweeper')  # 扫雷
# nonebot.load_plugin('nonebot_plugin_simplemusic')  # 点歌
# nonebot.load_plugin('nonebot_plugin_miragetank')  # 幻影坦克
# nonebot.load_plugin("nonebot_plugin_code")  # 在线代码

# nonebot.load_plugin("nonebot_plugin_questionAndAnswer")
# nonebot.load_plugin("nonebot_plugin_txt2img")  # 文字转图片
# nonebot.load_plugin("nonebot_plugin_boardgame")  # 五子棋围棋黑白棋
# nonebot.load_plugin("nonebot_plugin_navicat")  # 数据库
# nonebot.load_plugin("nonebot_plugin_cchess")  # 象棋
# nonebot.load_plugin("nonebot_plugin_guess")  # 猜猜看
# nonebot.load_plugin("nonebot_plugin_remake")
# nonebot.load_plugin('nonebot_plugin_weather_lite')  # 天气
# onebot.load_plugin("nonebot_plugin_heweather")  # 和风天气
# nonebot.load_plugin("nonebot_plugin_word_bank2")  # 无数据库的问答插件
# nonebot.load_plugin("nonebot_plugin_localstore")
# nonebot.load_plugin("nonebot_plugin_datastore")
# nonebot.load_plugins("src/plugins")

# Please DO NOT modify this file unless you know what you are doing!
# As an alternative, you should use command `nb` or modify `pyproject.toml` to load plugins
nonebot.load_from_toml("pyproject.toml")

# Modify some config / config depends on loaded configs
#
# config = driver.config
# do something...


if __name__ == "__main__":
    nonebot.logger.warning(
        "Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
