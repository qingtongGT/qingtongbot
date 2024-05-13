from .urls import *


# 添加白名单
add_white = on_command("add_white", rule=check_Admin)
# 删除白名单
del_white = on_command("del_white", rule=check_Admin)


@add_white.handle()
async def _(event: GroupMessageEvent):
    id = event.get_message().extract_plain_text()[9:]  # 获取第9个字符后的信息
    for i in data_white:
        if i == id:
            await add_white.finish("白名单:" + id + "已存在!")
    with open(FILE_WHITE, 'w', encoding='utf-8') as file:
        data_white.update({id: ""})
        file.write(json.dumps(data_white, ensure_ascii=False))
        file.close()
        await add_white.finish("已添加白名单" + id + "!")


@del_white.handle()
async def _(event: GroupMessageEvent):
    id = event.get_message().extract_plain_text()[9:]  # 获取第9个字符后的信息
    for i in data_white:
        if i == id:
            with open(FILE_WHITE, 'w', encoding='utf-8') as file:
                del data_white[i]
                file.write(json.dumps(data_white, ensure_ascii=False))
                file.close()
                await del_white.finish("删除" + id + "成功!")
    await del_white.finish("未找到要删除的白名单:" + id)
