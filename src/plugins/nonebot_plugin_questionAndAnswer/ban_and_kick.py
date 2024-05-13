from .urls import *


# 艾特踢人
kick = on_command("kick", rule=check_Admin)
# 禁言别人
ban = on_command("ban", rule=check_Admin)
# 禁言自己
ban_self = on_command("ban_self")


@kick.got("ID", prompt="请发送qq号")
@kick.got("CONFIRM", prompt="是否确认踢出? YES or NO, \n若同时拒绝加群则直接回复:reject")
async def _(bot: Bot, event: GroupMessageEvent, id: str = ArgPlainText("ID"), confirm: str = ArgPlainText("CONFIRM")):
    confirm = confirm.lower()
    if not len(id):
        await kick.finish("请输入数字!")
    if confirm == "no":
        await kick.finish("已取消!id:" + id)
    if confirm == "reject":
        sleep(2)
        await bot.set_group_kick(group_id=event.group_id, user_id=int(id), reject_add_request=True)
        await kick.finish("已将" + id + "移出群聊!")
    elif confirm == "yes":
        sleep(2)
        await bot.set_group_kick(group_id=event.group_id, user_id=int(id))
        await kick.finish("已将" + id + "移出群聊!")
    else:
        await kick.finish("请输入正确的指令!")


@ban.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    Message = event.get_message().extract_plain_text()
    id = regex2(Message).str1
    time = regex2(Message).str2
    try:
        time = float(time)
    except Exception:
        await ban.finish("请输入数字!")
    time *= 60
    sleep(2)
    try:
        await bot.set_group_ban(group_id=event.group_id, user_id=int(id), duration=int(time))
    except Exception:
        await ban.finish("".join(re.findall("wording\\=(.*)\\>", traceback.format_exc(), re.S)))


@ban_self.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    time = event.get_message().extract_plain_text()[8:]
    try:
        time = int(time)
    except Exception:
        await ban.finish("请输入数字!")
    time *= 60
    sleep(2)
    try:
        await bot.set_group_ban(group_id=event.group_id, user_id=int(event.user_id), duration=time)
    except Exception:
        await ban.finish("".join(re.findall("wording\\=(.*)\\>", traceback.format_exc(), re.S)))
