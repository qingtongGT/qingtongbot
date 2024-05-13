from io import TextIOWrapper
import json
from pathlib import Path
import random
import re
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

PATH_ROOT = Path.cwd()  # 机器人根目录
PATH_DATA = PATH_ROOT / "data"  # 数据目录
FILE = PATH_DATA / "integral.json"  # integral.josn文件

with open(FILE, 'r', encoding='utf-8') as file:
    data = json.load(file)

rob = on_command("打劫", aliases={"抢劫"})


@rob.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    text = event.get_message().extract_plain_text()
    text = "".join(re.findall("\\d", text))
    rob_id = str(text)  # 打劫者id
    user_id = str(event.user_id)  # 被打劫者id

    if len(rob_id) < 9:  # 粗略筛选
        return
    if user_id == rob_id:  # 判断是否打劫本人
        await rob.finish("你怎么可以打劫自己呢!")

    # 查找用户是否有使用记录,若无则创建,初始为0
    flag = False
    for id in data:
        if id == user_id:
            flag = True
    if not flag:
        data.update({user_id: 0})

    # 查找被打劫用户是否有使用记录,若无则创建,并进行打劫操作
    for id in data:
        # 查找到被打劫用户
        if id == rob_id:
            # 进行积分加减操作
            with open(FILE, 'w', encoding='utf-8') as file:
                inte_user = data[user_id]  # 打劫方现有积分
                inte_rob = data[rob_id]  # 被打劫方现有积分
                del data[user_id]  # 删除打劫方
                del data[rob_id]  # 删除被打劫方
                await Random(bot, event, file, user_id, rob_id, inte_user, inte_rob)

    # 若没有查找到被打劫用户
    with open(FILE, 'w', encoding='utf-8') as file:
        inte_user = data[user_id]  # 打劫方现有积分
        del data[user_id]  # 删除打劫方
        await Random(bot, event, file, user_id, rob_id, inte_user, 0)


# 判断打劫是否成功
async def Random(bot: Bot, event: GroupMessageEvent, file: TextIOWrapper, user_id: str, rob_id: str, inte_user: int, inte_rob: int):
    """判断打劫是否成功

    参数:
        bot (Bot) 
        event (GroupMessageEvent) 
        file(TextIOWrapper) : 用户积分记录文件
        user_id (str): 打劫方id
        rob_id (str): 被打劫方id
        inte_user (int): 打劫方积分
        inte_rob (int): 被打劫方积分
    """
    # 随机获取一个-20到20之间的打劫积分数num
    num = 0
    while num == 0:
        num = int(random.uniform(-30, 30))
    if num > 0:  # 若随机数大于0则说明打劫成功
        data.update({user_id: inte_user + num*4})  # 对打劫方进行加积分操作
        data.update({rob_id: inte_rob - num})  # 对被打劫方进行减积分操作
        json.dump(data, file)
        await ban(bot, event, num, rob_id, True)  # 进行禁言操作
    else:  # 若随机数小于0则说明打劫失败
        data.update({user_id: inte_user + num})  # 对打劫方进行减积分操作
        data.update({rob_id: inte_rob - num/2})  # 对被打劫方进行加积分操作
        json.dump(data, file)
        await ban(bot, event, num, rob_id, False)  # 进行禁言操作


# 构造禁言
async def ban(bot: Bot, event: GroupMessageEvent, num, rob_id: str, isSuccess: bool):
    """构造禁言

    参数:
        bot (Bot)
        event (GroupMessageEvent)
        num : 增加或扣除的积分
        rob_id (str) : 被打劫方id
        isSuccess(bool) : 是否打劫成功
    """
    if isSuccess:  # 若打劫成功
        if not rob_id == bot.self_id:
            await bot.set_group_ban(group_id=event.group_id, user_id=int(rob_id), duration=(num)*2)
            await rob.finish("打劫成功! 奖励:禁言对方" + str((num)*2) + "秒!" + "对方失去" + str(num) + "积分,你获得" + str(num*4) + "积分", at_sender=True)
        else:
            await rob.finish("打劫成功!" + "对方失去" + str(num) + "积分,你获得" + str(num*2.5) + "积分", at_sender=True)
    else:  # 若打劫失败
        await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=(-num)*6)
        await rob.finish("打劫失败! 惩罚:被禁言" + str((-num)*6) + "秒! 休息一下吧~" + "你失去" + str(-num) + "积分，对方获得" + str(-num/2) + "积分", at_sender=True)


# 显示积分
get_integral = on_command(
    "显示积分", aliases={"查看积分", "查询积分", "积分查询", "积分查看", "积分显示"})


@get_integral.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # 查找是否有使用记录,若找到则发送,否则创建,初始值为0
    for id in data:
        if str(id) == str(event.user_id):
            await get_integral.finish("积分为:"+str(data[id]), at_sender=True)
    # 未查找到,初始化用户积分
    with open(FILE, 'w', encoding='utf-8') as file:
        data.update({str(event.user_id): 0})
        json.dump(data, file)
    await bot.send(event, "积分为:0", at_sender=True)

# 天梯
rank = on_command("天梯", aliases={"排行榜", "排行"})


@rank.handle()
async def _(data=data):
    data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    msg = ""
    for i in range(5):
        msg += "第"+str(i+1)+"名: " + \
            str(data[i][0])+" 积分:" + \
            str(int(data[i][1]))+"\n"
    await rank.finish(msg)

# 负豪榜
_rank = on_command("负豪榜", aliases={"地梯"})


@_rank.handle()
async def _ (data=data):
    data = sorted(data.items(), key=lambda x: x[1])
    msg = ""
    for i in range(5):
        msg += "第"+str(i+1)+"名: " + \
            str(data[i][0])+" 积分:" + \
            str(int(data[i][1]))+"\n"
    await _rank.finish(msg)

# 查询他人积分
get_otherInte = on_command("查询")


@get_otherInte.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    other_id = str(event.get_message().extract_plain_text()[2:])
    if len(other_id) < 8:
        return
    user_info = await bot.get_group_member_info(
        group_id=event.group_id, user_id=int(other_id))
    for id in data:
        if id == other_id:
            await get_otherInte.finish(user_info['card'] or user_info['nickname'] + "积分为:" + str(data[id]))
    # 若没有查找到被打劫用户
    with open(FILE, 'w', encoding='utf-8') as file:
        data.update({other_id: 0})
        json.dump(data, file)
    await get_otherInte.finish(user_info['card'] or user_info['nickname'] + "积分为:0")
