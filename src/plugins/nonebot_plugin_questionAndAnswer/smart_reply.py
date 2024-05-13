from .urls import *

# ai回复
ai = on_message(rule=to_me(), priority=99)
# 戳一戳
poke = on_notice(rule=to_me(), block=False)
emotion = on_command("情绪分析")


@ai.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # 获取消息文本
    msg = str(event.get_message())
    # 去掉带中括号的内容(去除cq码)
    msg = re.sub(r"\[.*?\]", "", msg)
    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
    if (not msg) or msg.isspace() or msg in [
        "你好啊",
        "你好吖",
        "在咩",
        "在不在",
        "在",
    ]:
        await ai.finish(Message(random.choice(hello__reply)))
    # 获取用户nickname
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    # 从字典里获取结果
    result = await get_chat_result(msg,  nickname)  # type: ignore
    # 如果词库没有结果，则调用qingyunke获取智能回复
    if result == None:
        url = f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}"
        message = await get_reply(url)
        if random.random() < 0.5:
            sleep(1)
            await ai.finish(message=message)
        else:
            if isinstance(event, GroupMessageEvent):
                await bot.send_msg(message_type='group', group_id=event.group_id, message=f'[CQ:tts,text=' + message + ']')
                return
            else:
                await bot.send_msg(message_type='private', group_id=event.user_id, message=f'[CQ:tts,text=' + message + ']')
                return
    if random.random() < 0.5:
        sleep(1)
        await ai.finish(result)
    else:
        if isinstance(event, GroupMessageEvent):
            await bot.send_msg(message_type='group', group_id=event.group_id, message=f'[CQ:tts,text=' + result + ']')
            return
        else:
            await bot.send_msg(message_type='private', group_id=event.user_id, message=f'[CQ:tts,text=' + result + ']')
            return


@poke.handle()
async def _poke_event(bot: Bot, event: PokeNotifyEvent):
    if event.is_tome:
        sleep(2)
        # 50%概率回复莲宝的藏话
        if random.random() < 0.5:
            # 发送语音需要配置ffmpeg, 这里try一下, 不行就随机回复poke__reply的内容
            try:
                await poke.send(MessageSegment.record(Path(aac_file_path)/random.choice(aac_file_list)))
            except:
                await poke.send(message=f"{random.choice(poke__reply)}")
        # 随机回复poke__reply的内容
        else:
            if random.random() < 0.5:
                await poke.finish(f"{random.choice(poke__reply)}")
            else:
                if isinstance(event, GroupMessageEvent):
                    await bot.send_msg(message_type='group', group_id=event.group_id, message=f'[CQ:tts,text=' + f"{random.choice(poke__reply)}" + ']')
                    return
                else:
                    await bot.send_msg(message_type='private', group_id=event.user_id, message=f'[CQ:tts,text=' + f"{random.choice(poke__reply)}" + ']')
                    return


@emotion.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    text = event.get_message().extract_plain_text()[4:]
    if not text:
        await emotion.finish("请在后面加上要分析的内容!")
    request_url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/emotion'
    access_token = '24.0d37a30cbe03b42d25c2a0782d855314.2592000.1669901409.282335-28197966'
    url = request_url + '?access_token=' + access_token
    headers = {'content-type': 'application/json'}
    params = {
        "scene": "talk",
        "text": text
    }
    response = requests.get(url=url, params=params, headers=headers)
    emotion_first = {
        'pessimistic': '负向',
        'neutral': '中性',
        'optimistic': '正向'
    }

    emotion_second = {
        'thankful': '感谢',
        'happy': ' 愉快',
        'complaining': '抱怨',
        'angry': '愤怒',
        'like': '喜爱',
        'happy': '愉快',
        'angry': '愤怒',
        'disgusting': '厌恶',
        'fearful': '恐惧',
        'sad': '悲伤'
    }
    count = 1
    result = "推荐回复:"
    msg = ''
    for ele in response.json()['items']:
        if ele['replies']:
            msg = ele['replies'][0]
    if not msg:
        if isinstance(event, GroupMessageEvent):
            nickname = event.sender.card or event.sender.nickname
        else:
            nickname = event.sender.nickname
        # 从字典里获取结果
        msg = await get_chat_result(text,  nickname)    # type:ignore
        # 如果词库没有结果，则调用qingyunke获取智能回复
        if msg == None:
            url = f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={text}"
            msg = await get_reply(url)
    result += msg + '\n\n'
    for ele in response.json()['items']:
        result += str(count) + '. '
        prob = round(ele['prob'], 4)
        prob *= 100
        result += '一级分类:' + '\n'
        for ele_emo in emotion_first:
            if ele_emo == ele['label']:
                result += '情绪为' + emotion_first[ele_emo] + \
                    '的概率为:' + str(prob) + '%'
        if ele['subitems']:
            prob = round(ele['subitems'][0]['prob'], 4)
            prob *= 100
            result += '\n' + '二级分类:' + '\n'
            for ele_emo in emotion_second:
                if ele_emo == ele['subitems'][0]['label']:
                    result += '情绪为' + \
                        emotion_second[ele_emo] + \
                        '的概率为:' + str(prob) + '%'
        if count != 3:
            result += '\n\n'
        count += 1
    msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=result, auto_escape=False))['message_id']
    dict_msg_id.update({time.time(): {event.group_id: msg_id}})
