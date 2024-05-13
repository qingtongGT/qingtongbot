from .urls import *

set_special_title = on_command("给头衔")


@set_special_title.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    title = event.get_message().extract_plain_text()[3:]
    await bot.set_group_special_title(group_id=event.group_id, user_id=event.user_id, special_title=title, duration=-1)
    return


set_bot_special_title = on_command("给bot头衔", rule=check_SuperUser)


@set_bot_special_title.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    title = event.get_message().extract_plain_text()[6:]
    await bot.set_group_special_title(group_id=event.group_id, user_id=event.self_id, special_title=title, duration=-1)
    return
