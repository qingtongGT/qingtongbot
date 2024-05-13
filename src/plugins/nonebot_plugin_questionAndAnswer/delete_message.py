from .urls import *

delete_message = on_command("撤回", rule=check_Admin)


@delete_message.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await bot.delete_msg(message_id=event.reply.message_id)  # type: ignore
