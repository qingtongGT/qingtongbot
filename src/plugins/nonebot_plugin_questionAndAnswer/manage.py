from .urls import *


# 处理加群请求
set_group_request = on_request()
# 文字转语音
speak = on_command("speak")
# 发送入群欢迎
send_welcome = on_notice()
# 定时发送早安消息
refresh_goodmorning_time = on_command("刷新早安时间", rule=check_Admin)
# 查询信息
search = on_command("查询")
# 自助艾特全体
at_all_member = on_command("全体成员")


# 防刷屏
async def write_msg(
    bot: Bot,
    int_group_id: int,
    int_user_id: int,
    msg,
    int_msg_id: int
):
    group_id = str(int_group_id)
    user_id = str(int_user_id)
    msg_id = str(int_msg_id)
    flag_group = False
    for ele_group_id in data_message:   # 检索此群聊
        if ele_group_id == group_id:
            flag_group = True   # 找到该群
            flag_user = False
            # 检索此群聊下的此用户
            for ele_user_id in data_message[group_id]:
                if ele_user_id == user_id:
                    # 检索此用户的消息
                    for ele_msg in data_message[group_id][user_id]:
                        if ele_msg == msg:  # 找到此消息
                            await bot.delete_msg(message_id=data_message[group_id][user_id][msg])
                            with open(FILE_MESSAGE, 'w', encoding='utf-8') as file:
                                data_message[group_id][user_id][msg] = msg_id
                                file.write(json.dumps(
                                    data_message, ensure_ascii=False))
                                file.close()
                            return
                        else:  # 若没有查找到相同消息, 则删除之前的消息, 并记录此消息
                            with open(FILE_MESSAGE, 'w', encoding='utf-8') as file:
                                del data_message[group_id][user_id]
                                data_message[group_id].update(
                                    {user_id: {msg: msg_id}})
                                file.write(json.dumps(
                                    data_message, ensure_ascii=False))
                                file.close()
                            return
            if flag_user == False:   # 若未查找到此用户, 则新建用户
                with open(FILE_MESSAGE, 'w', encoding='utf-8') as file:
                    data_message[group_id].update({user_id: {msg: msg_id}})
                    file.write(json.dumps(
                        data_message, ensure_ascii=False))
                    file.close()
                return
    # 若未查找到此群聊, 则新建群聊
    if flag_group == False:
        with open(FILE_MESSAGE, 'w', encoding='utf-8') as file:
            data_message.update({group_id: {user_id: {msg: msg_id}}})
            file.write(json.dumps(data_message, ensure_ascii=False))
            file.close()
        return


# 自动撤回自己发出的消息
async def auto_del_msg(bot: Bot, event: GroupMessageEvent, dict_msg_id: dict, time_now: float):
    for ele_time in list(dict_msg_id.keys()):
        if time_now - ele_time > 120:
            for group_id in list(dict_msg_id[ele_time].keys()):
                if group_id == event.group_id:
                    try:
                        await bot.delete_msg(message_id=dict_msg_id[ele_time][group_id])
                        del dict_msg_id[ele_time]
                    except Exception:
                        del dict_msg_id[ele_time]


@set_group_request.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    user_id = event.user_id
    for ele in data_reject_group_request:
        if ele == user_id:
            return
    user_info = await bot.get_stranger_info(user_id=user_id)
    if user_info['level'] < 16:
        sleep(5)
        await bot.set_group_add_request(flag=event.flag, sub_type='add', approve=False, reason='小号吗')
        with open(FILE_REJRCT_GROUP_REQUEST, 'w') as file:
            data_reject_group_request.update({user_id: ""})
            json.dump(data_reject_group_request, file)
            file.close()


@speak.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    text = event.get_message().extract_plain_text()[5:]
    await bot.send_msg(message_type='group', group_id=event.group_id, message=f'[CQ:tts,text=' + text + ']')


@send_welcome.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.group_id != 293102163:
        if event.group_id != 535768255:
            return
    msg = '欢迎 ' + f'[CQ:at,qq=' + str(event.user_id) + '] (' + str(
        event.user_id) + ')入群!发送detail或image可以向我提问, 也可以艾特我发起聊天, 也可以戳一戳我喔'
    await bot.send_msg(message_type='group', group_id=event.group_id, message=msg, auto_escape=False)


@refresh_goodmorning_time.handle()
async def timing_goodmorning(bot: Bot):
    time_now = time.time()
    with open(FILE_GOODMORNING, 'w') as file:
        data_goodmoring['time'] = time_now
        json.dump(data_goodmoring, file)
        file.close()
    path = os.path.join(PATH_IMAGES, "群友怪话")  # 打开路径的文件夹
    img1 = path + '/' + random.choice(os.listdir(path))  # 从路径随机提取一张图片
    img2 = path + '/' + random.choice(os.listdir(path))  # 从路径随机提取一张图片
    img3 = path + '/' + random.choice(os.listdir(path))  # 从路径随机提取一张图片
    message = '群u们早安!今天又是元气满满的一天哦!请查收今日的群友怪话:'
    await bot.send_msg(message_type='group', group_id=293102163, message=message + MessageSegment.image('file:///'+img1))
    await bot.send_msg(message_type='group', group_id=624969484, message=message + MessageSegment.image('file:///'+img2))
    await bot.send_msg(message_type='group', group_id=535768255, message=message + MessageSegment.image('file:///'+img3))


@search.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    id = event.get_message().extract_plain_text()[2:]
    try:
        member_info = await bot.get_group_member_info(group_id=event.group_id, user_id=int(id))
        await search.finish("nickname: " + member_info['nickname'] + '\n' + 'card:' + member_info['card'])
    except Exception:
        await search.finish("".join(re.findall("wording\\=(.*)\\>", traceback.format_exc(), re.S)))


@at_all_member.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    list_group_id = [481048845, 293102163, 895069482, 549459511]
    # 检查是否可以 @全体成员
    if (await bot.get_group_at_all_remain(group_id=event.group_id))['can_at_all'] == False:
        await at_all_member.finish("机器人今日剩余次数已用尽!")
    # 检查是否在可触发群聊内
    for ele_group_id in list_group_id:
        if ele_group_id == event.group_id:
            role = (await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id, no_cache=False))['role']
            if role == 'admin' or role == 'owner':
                await at_all_member.finish("管理员自己艾特")
            else:
                # 获取Bot 当天剩余 @全体成员 次数
                count = (await bot.get_group_at_all_remain(group_id=event.group_id))['remain_at_all_count_for_uin']
                await bot.send_group_msg(group_id=event.group_id, message=f'[CQ:at,qq=all]', auto_escape=False)
                await at_all_member.finish("机器人今日剩余次数: " + str(count))
