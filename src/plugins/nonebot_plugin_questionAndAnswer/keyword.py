from .urls import *


# 添加广告关键词
add_keyword = on_command("add_keyword", rule=check_Admin)
# 删除广告关键词
del_keyword = on_command("del_keyword", rule=check_Admin)


@add_keyword.handle()
async def _(event: GroupMessageEvent):
    keyword = event.get_message().extract_plain_text()[11:]
    for k in data_keyword:
        if k == keyword:
            await add_keyword.finish("关键词" + keyword + "已存在~")
    with open(FILE_KEYWORD, 'w', encoding='utf-8') as file:
        data_keyword.update({keyword: ""})
        file.write(json.dumps(data_keyword, ensure_ascii=False))
        file.close()
    await add_keyword.finish("添加关键词" + keyword + "成功!")


@del_keyword.handle()
async def _(event: GroupMessageEvent):
    keyword = event.get_message().extract_plain_text()[11:]
    for k in data_keyword:
        if k == keyword:
            with open(FILE_KEYWORD, 'w', encoding='utf-8') as file:
                del data_keyword[k]
                file.write(json.dumps(data_keyword, ensure_ascii=False))
                file.close()
                await del_keyword.finish("删除关键词" + keyword + "成功!")
    await del_keyword.finish("未找到想删除的关键词:" + keyword)
