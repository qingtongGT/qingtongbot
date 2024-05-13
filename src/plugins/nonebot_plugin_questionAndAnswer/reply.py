from .urls import *
from .image import *
from .manage import(
    write_msg,
    auto_del_msg
)

# 匹配词条并回答问题
MESSAGE = on_command("", priority=100, block=True)
send_interaction = on_command("*", aliases={"＊"})
pre_send_someImage = on_command(".")
# 增加词条
add_interaction = on_command("add词条", rule=check_Admin)
# 更新词条
up_interaction = on_command("up词条", rule=check_Admin)
# 追加词条
append_interaction = on_command("append词条", rule=check_Admin)
# 删除词条
del_interaction = on_command("del词条", rule=check_Admin)
# 添加自动回复
add_autoReply = on_command("add回复", rule=check_Admin)
# 更新自动回复
up_autoReply = on_command("up回复", rule=check_Admin)
# 追加自动回复
append_autoReply = on_command("append回复", rule=check_Admin)
# 删除自动回复
del_autoReply = on_command("del回复", rule=check_Admin)


@MESSAGE.handle()
async def _(bot: Bot, event):
    Message = event.get_message().extract_plain_text()
    # 记录消息
    # await write_msg(bot, event.group_id, event.user_id, Message, event.message_id)

    time_now = time.time()

    # 拦截违禁消息
    # for data in data_keyword:
    #     if re.findall(data, Message):
    #         await del_msg(bot, event, Message)  # 撤回违禁消息
    #         return

    # 自动撤回自己发出的消息
    if event.message_type == 'group':
        await auto_del_msg(bot, event, dict_msg_id, time_now)

    # 查询interaction消息
    if Message.lower() == "detail" or Message.lower() == "details":
        path = os.path.join(PATH_TXT2IMG, "interaction")
        if not os.path.exists(path):
            await MESSAGE.finish("喵(∩。˙ω˙。)⊃━♡°.*˙。")
        file = path + '/' + "".join(os.listdir(path))
        if event.message_type == 'group':
            msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=MessageSegment.image('file:///'+file) + ""))['message_id']
            dict_msg_id.update({time_now: {event.group_id: msg_id}})
        else:
            await bot.send_msg(message_type='private', user_id=event.user_id, message=MessageSegment.image('file:///'+file) + "")

    # 查询someImage
    if Message.lower() == "image":
        path = os.path.join(PATH_TXT2IMG, "someImage")
        if not os.path.exists(path):
            await MESSAGE.finish("喵喵ヾ(•ω•`)o")
        file = path + '/' + "".join(os.listdir(path))
        if event.message_type == 'group':
            msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=MessageSegment.image('file:///'+file) + ""))['message_id']
            dict_msg_id.update({time_now: {event.group_id: msg_id}})
        else:
            await bot.send_msg(message_type='private', user_id=event.user_id, message=MessageSegment.image('file:///'+file) + "")

    # 查询自动回复列表
    if Message.lower() == "autoreply":
        await send_forward_msg(bot, event, "自动回复列表", bot.self_id, data_autoReply)

    # 查询管理员列表
    if Message == "get_admins":
        await send_forward_msg(bot, event, "管理员名单", bot.self_id, data_admins)

    # 查询白名单
    if Message == "get_white":
        await send_forward_msg(bot, event, "白名单", bot.self_id, data_white)

    # 查询违禁词列表
    if Message == "get_keyword":
        await send_forward_msg(bot, event, "违禁词", bot.self_id, data_keyword)

    # 遍历是否是interaction消息,是则发送
    for data in data_interaction:
        if(data == Message):
            sleep(1)
            if event.message_type == 'group':
                msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=data_interaction[data]))['message_id']
                dict_msg_id.update({time_now: {event.group_id: msg_id}})
            else:
                await MESSAGE.send(data_interaction[data])

    # 遍历是否是someImage消息
    for data in data_someImage:
        if(data == Message):
            sleep(1)
            await send_someImage(bot, event, data)
            return

    # 判断是否需要自动回复
    for data in data_autoReply:  # 遍历所有回复的匹配规则
        match_message = re.findall(data, Message)   # 将文本按照匹配规则匹配为list
        # 将匹配规则匹配为list文字
        match_ques = re.findall("[^\\(\\)\\.\\*\\\]", data)  # type:ignore
        # 将list转换为str
        str_message = ""
        str_ques = ""
        for m in match_message:
            str_message += "".join(m)
        for m in match_ques:
            str_ques += "".join(m)
        # 查询是否是interaction消息,是则发送
        for ques in data_interaction:
            if(ques == str_message):
                await MESSAGE.send(data_interaction[ques])
        # 查询是否是someImage消息
        for image in data_someImage:
            if(image == str_message):
                await send_someImage(bot, event, image)
                return
        # 查询是否有匹配的自动回复
        if(str_message == str_ques):
            sleep(1)
            await MESSAGE.finish(data_autoReply[data])


@send_interaction.handle()
async def _(bot: Bot, event: MessageEvent):
    await send(bot, event, data_interaction, "interaciton")


@pre_send_someImage.handle()
async def _(bot: Bot, event: MessageEvent):
    await send(bot, event, data_someImage, "someImage")


@ add_interaction.handle()
async def _(bot: Bot, event: MessageEvent):
    await add_reply(bot, event, data_interaction, FILE_INTERACTION, IMAGE_INTERACTION, "interaction.png")


@up_interaction.handle()
async def _(bot: Bot, event: MessageEvent):
    await up_reply(bot, event, data_interaction, FILE_INTERACTION)


@append_interaction.handle()
async def _(bot: Bot, event: MessageEvent):
    await append_reply(bot, event, data_interaction, FILE_INTERACTION)


@del_interaction.handle()
async def _(bot: Bot, event: MessageEvent):
    await del_reply(bot, event, data_interaction, FILE_INTERACTION, IMAGE_INTERACTION, "interaction.png")


@add_autoReply.handle()
async def _(bot: Bot, event: MessageEvent):
    await add_reply(bot, event, data_autoReply, FILE_AUTOREPLY, "", "")


@up_autoReply.handle()
async def _(bot: Bot,  event: MessageEvent):
    await up_reply(bot, event, data_autoReply, FILE_AUTOREPLY)


@append_autoReply.handle()
async def _(bot: Bot, event: MessageEvent):
    await append_reply(bot, event, data_autoReply, FILE_AUTOREPLY)


@del_autoReply.handle()
async def _(bot: Bot, event: MessageEvent):
    await del_reply(bot, event, data_autoReply, FILE_AUTOREPLY, "", "")


# 发送前的合并转发操作
async def send_forward_msg(
    bot: Bot,
    event: GroupMessageEvent,
    name,  # 机器人名字
    uin,  # 机器人id
    data,  # 消息内容
):
    def to_json(data):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": data}}

    messages = [to_json(msg) for msg in data]
    await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=messages)


# 遍历发送
async def send(bot: Bot, event, data: Any, type: str):
    num = event.get_message().extract_plain_text()[1:]  # 获取第1个字符后的信息
    count = 0  # 记录序号变化
    for d in data:  # 遍历json, 若找到序号则发送
        count += 1
        if(str(count) == num):
            sleep(1)
            if type == "someImage":
                await send_someImage(bot, event, d)
                # 尝试发送词条, 若无同名图则返回
                try:
                    if event.message_type == 'group':
                        msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=data[d]))['message_id']
                        dict_msg_id.update(
                            {time.time(): {event.group_id: msg_id}})
                    else:
                        await MESSAGE.send(data[d])
                except Exception:
                    return

            else:
                if event.message_type == 'group':
                    msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=data[d]))['message_id']
                    dict_msg_id.update({time.time(): {event.group_id: msg_id}})
                else:
                    await MESSAGE.send(data[d])
                # 尝试发送图片, 若无同名图则返回
                try:
                    await send_someImage(bot, event, d)
                except Exception:
                    return


# 发送someImage
async def send_someImage(bot: Bot, event, data: str):
    path = os.path.join(PATH_SOMEIMAGES, data)  # 打开路径的文件夹
    if not os.path.exists(path):  # 查找路径是否存在
        return
    file = path + '/' + random.choice(os.listdir(path))  # 从路径随机提取一张图片
    sleep(1)
    if event.message_type == 'group':
        msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=MessageSegment.image('file:///'+file) + ''))['message_id']
        dict_msg_id.update({time.time(): {event.group_id: msg_id}})
    else:
        await MESSAGE.send(MessageSegment.image('file:///'+file) + '')
    return


# 添加回复
async def add_reply(bot: Bot, event: MessageEvent, data: Any, FILE: Path, IMAGE, png: str):
    Message = event.get_message().extract_plain_text()
    ques = regex2(Message).str1
    ans = regex2(Message).str2
    # 遍历字典查询词条是否重复
    for q in data:
        if(q == ques):
            await bot.send(event,  ques + " 已存在!ヽ(*。>Д<)o゜")
            return
    with open(FILE, 'w', encoding='utf-8') as file:
        data.update({ques: ans})
        file.write(json.dumps(data, ensure_ascii=False))
        file.close()

    if IMAGE == IMAGE_INTERACTION:
        # 更新interaction图片
        await update_image(bot, event, IMAGE, png)
    await bot.send(event, ques + " 添加成功~ (*˘︶˘*).。.:*♡")


# 更新回复
async def up_reply(bot: Bot, event: MessageEvent, data: Any, FILE: Path):
    Message = event.get_message().extract_plain_text()
    ques = regex2(Message).str1
    ans = regex2(Message).str2
    for q in data:
        if q == ques:
            with open(FILE, 'w', encoding='utf-8') as file:
                data[q] = ans
                file.write(json.dumps(data, ensure_ascii=False))
                file.close()
            await bot.send(event, q + " 更新成功~ (。’▽’。)♡")
            return
    await bot.send(event, "未找到 " + ques + " ~ ( ๑ŏ ﹏ ŏ๑ )")


# 追加回复
async def append_reply(bot: Bot, event: MessageEvent, data: Any, FILE: Path):
    Message = event.get_message().extract_plain_text()
    ques = regex2(Message).str1
    ans = regex2(Message).str2
    for q in data:
        if q == ques:
            with open(FILE, 'w', encoding='utf-8') as file:
                ans_old = data[ques]  # 提取原答案
                ans_old += "\n"
                ans_old += ans
                data[ques] = ans_old
                file.write(json.dumps(data, ensure_ascii=False))
                file.close()
            await bot.send(event, q + "追加成功~ (。’▽’。)♡")
            return
    await bot.send(event, "未找到" + ques + "~ ( ๑ŏ ﹏ ŏ๑ )")


# 删除回复
async def del_reply(bot: Bot, event: MessageEvent, data: Any, FILE: Path, IMAGE, png: str):
    ques = event.get_message().extract_plain_text()[5:]
    for q in data:
        if q == ques:  # 若找到要删除的词条
            with open(FILE, 'w', encoding='utf-8') as file:
                del data[ques]
                file.write(json.dumps(data, ensure_ascii=False))
                file.close()
            if IMAGE == IMAGE_INTERACTION:
                # 更新interaction图片
                await update_image(bot, event, IMAGE, png)
            await bot.send(event, q + " 删除成功(*˘︶˘*).。.:*♡")
            return
    await bot.send(event, "未找到: " + ques + " ~Σ(ŎдŎ|||)ﾉﾉ")


# 撤回违禁消息
async def del_msg(bot: Bot, event: MessageEvent, Message: str):
    await bot.delete_msg(message_id=event.message_id)  # 撤回消息
    # 遍历消息, 将检测到违禁词库词都替换掉
    for data in data_keyword:
        # 使用正则搜索单个违禁词
        if re.findall(data, Message, re.S):
            match_data = "".join(re.findall(
                "[^\\(\\)\\.\\*\\\]", data))  # type: ignore
            # 将单个违禁词的每个字都替换
            for data in match_data:
                Message = Message.replace(data, "*")
    if Message.count('*') >= 8:
        return
    sender_name = event.sender.card or event.sender.nickname    # 获取发送者群名片或昵称
    # 发送被屏蔽后的消息内容
    await bot.send(event, str(sender_name) + "(" + str(event.user_id) + "): " + Message)
