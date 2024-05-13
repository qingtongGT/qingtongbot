from .urls import *


# 增加管理员
add_admins = on_command("add_admins", rule=check_SuperUser)
# 删除管理员
del_admins = on_command("del_admins", rule=check_SuperUser)


@add_admins.handle()
async def _(event: GroupMessageEvent):
    id = event.get_message().extract_plain_text()[10:]  # 获取第10个字符后的信息
    for aid in data_admins:
        if aid == id:
            await add_admins.finish("管理员" + id + "已存在!")
    with open(FILE_ADMINS, 'w', encoding='utf-8') as file:
        data_admins.update({id: ""})
        json.dump(data_admins, file)
        file.close()
        await add_admins.finish("管理员" + id + "添加成功!")


@del_admins.handle()
async def _(event: GroupMessageEvent):
    id = event.get_message().extract_plain_text()[10:]  # 获取第10个字符后的信息
    for aid in data_admins:
        if aid == id:  # 若找到要删除的管理员
            with open(FILE_ADMINS, 'w', encoding='utf-8') as file:
                del data_admins[id]
                json.dump(data_admins, file)
                file.close()
            await del_admins.finish("删除管理员" + id + "成功!")
    await del_admins.finish("未找到要删除的管理员" + id + "!")
