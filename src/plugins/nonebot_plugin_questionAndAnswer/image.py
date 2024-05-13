from .urls import *

# 添加image
add_image = on_command("添加图片")
# 添加someImage
add_someImage = on_command("add_someImage", rule=check_Admin)
# 发送image
send_image = on_command('来')
# 删除单张someImage
del_someImage = on_command("del_someImage", rule=check_Admin)
# 删除单张image
del_image = on_command("del_image", rule=check_Admin)
# 删除所有someImage
del_allSomeImage = on_command(
    "del_allSomeImage", rule=check_Admin)
# 删除所有image
del_allImage = on_command("del_allImage", rule=check_Admin)


@add_image.handle()
async def _(bot: Bot, event: MessageEvent):
    msg = event.get_message().extract_plain_text()
    name = msg[msg.find('添加图片')+4:].strip()
    await addImage(bot, event, name, PATH_IMAGES)


# 先对json文件进行更新
@add_someImage.handle()
async def _(bot: Bot, event: MessageEvent):
    Message = event.get_message().extract_plain_text()
    name = Message[Message.find('add_someImage')+13:].strip()

    # 查询someImage.json是否存在该同名图片,若不存在则更新json文件
    for n in data_someImage:
        if n == name:
            await addImage(bot, event, name, PATH_SOMEIMAGES)  # 添加图片
    with open(FILE_SOMEIMAGE, 'w', encoding='utf-8') as file:
        data_someImage.update({name: ""})
        file.write(json.dumps(data_someImage, ensure_ascii=False))
        file.close()
    await addImage(bot, event, name, PATH_SOMEIMAGES)  # 添加图片


# 图片添加操作
async def addImage(
        bot: Bot,
        event,
        name: str,
        PATH: Path
):
    """添加图片

    参数:
        name (str): 图片名字
        PATH (Path): 图片路径
    """
    path = os.path.join(PATH, name)
    if not os.path.exists(path):
        os.makedirs(path)
    url = re.findall('url\\=(.*)\\]',
                     str(event.reply.message))  # type: ignore
    image = re.findall('file\\=(.*\\.jpg)',
                       str(event.reply.message)) or re.findall('file\\=(.*\\.gif)',
                                                               str(event.reply.message)) or re.findall('file\\=(.*\\.png)',
                                                                                                       str(event.reply.message))
    conn = urllib.request.urlopen(url[0])
    f = open(os.path.join(path, image[0]), 'wb')
    f.write(conn.read())
    f.close()
    if PATH == PATH_SOMEIMAGES:
        await update_image(bot, event, IMAGE_SOMEIMAGE, "someImage.png")
        await add_someImage.finish("已添加" + name + "~(∗ᵒ̶̶̷̀ω˂̶́∗)੭₎₎̊₊♡")
    elif PATH == PATH_IMAGES:
        await add_image.finish("已添加" + name + "~(∗ᵒ̶̶̷̀ω˂̶́∗)੭₎₎̊₊♡")


@send_image.handle()
async def _(event: PrivateMessageEvent):
    if len(event.get_message().extract_plain_text()) < 3:
        return
    name = event.get_message().extract_plain_text()[2:]  # 获取第2个字符后的信息
    path = os.path.join(PATH_IMAGES, name)  # 打开路径的文件夹
    if not os.path.exists(path):  # 查找路径是否存在
        return
    file = path + '/' + random.choice(os.listdir(path))  # 从路径随机提取一张图片
    sleep(1)
    await send_image.finish(MessageSegment.image('file:///'+file))


@del_someImage.handle()
async def _(bot: Bot, event: MessageEvent):
    Message = event.get_message().extract_plain_text()
    name = Message[Message.find('del_someImage')+13:].strip()  # 获取图片文件夹名字
    path = os.path.join(PATH_SOMEIMAGES, name)  # 打开路径文件夹
    await delImage(bot, event, path, name)


@del_image.handle()
async def _(bot: Bot, event: MessageEvent):
    Message = event.get_message().extract_plain_text()
    name = Message[Message.find('del_image')+9:].strip()  # 获取图片文件夹名字
    path = os.path.join(PATH_IMAGES, name)  # 打开路径文件夹
    await delImage(bot, event, path, name)


# 删除单张图片
async def delImage(
    bot: Bot,
    event,
    path: str,
    name: str
):
    """删除单张图片

    参数:
        path (str) : 图片路径
        name (str) : 图片名字
    """
    # 判断名字是否为空
    if not len(name):
        return
    image = re.findall('file\\=(.*\\.jpg)',
                       str(event.reply.message)) or re.findall('file\\=(.*\\.gif)',
                                                               str(event.reply.message)) or re.findall('file\\=(.*\\.png)',
                                                                                                       str(event.reply.message))
    if image:
        file_name = os.path.join(path, image[0])
        try:
            os.remove(file_name)
        except FileNotFoundError:
            await bot.send(event, "未找到要删除的文件!")
            return
        # 若文件夹为空则删除
        try:
            os.rmdir(path)
            await bot.send(event, "删除所有" + name + "成功!")
        except Exception:
            await bot.send(event, "删除" + name + "成功!")
        finally:
            return
    else:
        await bot.send(event, "请回复图片!")


@del_allSomeImage.got("NAME", prompt="请输入图片名字")
@del_allSomeImage.got("CONFIRM", prompt="确认删除吗?回复:YES or NO")
async def _(bot: Bot, event: MessageEvent, name: str = ArgPlainText("NAME"), confirm: str = ArgPlainText("CONFIRM")):
    confirm = confirm.upper()
    if confirm == "NO":
        await del_allSomeImage.finish("已取消删除" + name)
    elif confirm == "YES":
        path = os.path.join(PATH_SOMEIMAGES, name)  # 打开路径文件夹
        # 更新image图片
        for n in data_someImage:
            if n == name:  # 若找到要删除的图片
                with open(FILE_SOMEIMAGE, 'w', encoding='utf-8') as file:
                    del data_someImage[n]
                    file.write(json.dumps(data_someImage, ensure_ascii=False))
                    file.close()
                # 更新image图片
                await update_image(bot, event, FILE_SOMEIMAGE, "someImage.png")
                await delAllImage(bot, event, path, name)  # 删除图片
                return  # 返回
        await del_allSomeImage.finish("未找到要删除的 " + name)
    else:
        await del_allSomeImage.finish("请输入正确的指令!")


@del_allImage.got("NAME", prompt="请输入图片名字")
@del_allImage.got("CONFIRM", prompt="确认删除吗?回复:YES or NO")
async def _(bot: Bot, event: MessageEvent, name: str = ArgPlainText("NAME"), confirm: str = ArgPlainText("CONFIRM")):
    confirm = confirm.upper()
    if confirm == "NO":
        await del_allImage.finish("已取消删除" + name)
    elif confirm == "YES":
        path = os.path.join(PATH_IMAGES, name)  # 打开路径文件夹
        await delAllImage(bot, event, path, name)
    else:
        await del_allImage.finish("请输入正确的指令!")


# 删除所有图片
async def delAllImage(
    bot: Bot,
    event: MessageEvent,
    path: str,
    name: str
):
    """删除所有图片

    参数:
        path (str) : 图片路径
        name (str) : 图片名字
    """
    if not os.path.exists(path):    # 检查路径是否存在
        await bot.send(event, "库存未找到" + name)
    try:
        shutil.rmtree(path)
        await bot.send(event, "删除所有" + name + "成功!")
    except Exception:
        await bot.send(event, "".join(re.findall("wording\\=(.*)\\>", traceback.format_exc(), re.S)))


# 更新图片
async def update_image(bot: Bot, event: MessageEvent, file: Path, type: str):
    """更新图片

    参数:
        file(Path) : image路径
        type(str) : image类型(interaction.png or someImage.png)
    """
    if os.path.exists(file):  # 删除旧的图片
        os.remove(file)

    list = []  # 字典通过该列表转换为字符串
    list_length = 0  # 记录列表条数
    img = Txt2Img(32)  # 数字表示字号
    string = "2023级福建师范大学迎新群:839652032\n"  # 图片内容字符串

    # 将字典转换为列表
    if type == "interaction.png":
        for data in data_interaction:
            list.append(data)
            list_length += 1
    elif type == "someImage.png":
        for data in data_someImage:
            list.append(data)
            list_length += 1
    else:
        await bot.send(event, "type参数有误!")
    # 将列表转换为字符串
    for i in range(list_length):
        string += str(i+1)
        string += ". "
        string += list[i]
        string += "\n"
    if type == "interaction.png":
        img.save("回复 '*'+问题序号 或问题", string, type)
    elif type == "someImage.png":
        img.save("回复 '.'+图片序号 或图片名", string, type)
    else:
        await bot.send(event, "type参数有误!")
