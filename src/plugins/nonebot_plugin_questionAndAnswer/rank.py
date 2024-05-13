from .urls import *

# 获取卷王排行榜
get_rank = on_command('oj题数')
# 今日题数
get_today_rank = on_keyword({"今日题数"})


# 递归获取榜单
async def get_next_soup(soup: BeautifulSoup) -> BeautifulSoup:
    pager__item = soup.select('span.pager__item.current')
    next_page = str(int(str(pager__item[0].contents[0])) + 1)
    url = 'https://oj.fjnuacm.top/d/junior/ranking?page=' + next_page
    next_soup = await url_to_soup(url)
    if next_soup.select('a.pager__item.next.link'):
        return BeautifulSoup(str(soup) + str(await get_next_soup(next_soup)), 'html.parser')
    else:
        return BeautifulSoup(str(soup) + str(next_soup), 'html.parser')


@get_rank.handle()
async def _get_rank(bot: Bot, event: GroupMessageEvent):
    start_time = time.time()
    global isGetTodayRank
    url = 'https://oj.fjnuacm.top/d/junior/ranking'
    try:
        soup = await url_to_soup(url)
        if soup.select('a.pager__item.next.link'):
            soup = await get_next_soup(soup)
    except Exception as e:
        await get_rank.finish(repr(e))
    user_name = soup.select('a.user-profile-name')   # 获取用户名
    user_id = soup.select('img.small')  # 获取带有用户id
    num = soup.select('td.col--ac')  # 获取ac题数Tag
    list_user_ojName = []  # 用户名
    list_user_id = []   # qq号
    list_user_card = []
    dict_user_name_and_num = {}  # 用户名和ac题数的字典
    dict_user_ojName_and_num = {}
    rank_length = 0
    # 将用户名中的空格和换行符去除
    logger.warning(len(soup))
    for ele in user_name:
        string = str(user_name[rank_length].string).strip()
        list_user_ojName.append(string)
        rank_length += 1

    # 获取qq号
    for i in range(rank_length):
        find_text = re.compile(r'\d+').findall(user_id[i].attrs['src'])
        if len(find_text) == 3 and find_text[2] == '160':
            list_user_id.append(find_text[1])
        else:
            list_user_id.append('none')

    # 将获取的qq号转换为昵称
    for i in range(rank_length):
        if list_user_id[i] == 'none':
            list_user_card.append(str(list_user_ojName[i]))
        else:
            try:
                ele_user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=int(list_user_id[i]), no_cache=False)
                if len(ele_user_info['card']):
                    list_user_card.append(ele_user_info['card'])
                elif len(ele_user_info['nickname']):
                    list_user_card.append(ele_user_info['nickname'])
                else:
                    list_user_card.append(
                        str(list_user_ojName[i]) + '(' + str(list_user_id[i]) + ')')
            except Exception:
                list_user_card.append(
                    str(list_user_ojName[i]) + '(' + str(list_user_id[i]) + ')')
    # 获取题数Tag中的题数
    for i in range(rank_length):
        ele = num[i].string
        dict_user_name_and_num.update(
            {list_user_card[i]: [int(ele), list_user_id[i]]})  # type: ignore
        dict_user_ojName_and_num.update(
            {list_user_ojName[i]: [int(ele), list_user_id[i]]})  # type: ignore
    # 根据题数从小到大排序用户
    listTuple_user_name_and_num = sorted(
        dict_user_name_and_num.items(), key=lambda x: x[1], reverse=True)
    listTuple_user_ojName_and_num = sorted(
        dict_user_ojName_and_num.items(), key=lambda x: x[1], reverse=True)
    # 发送天梯
    text = '      卷王天梯榜\n'
    for i in range(rank_max_length):
        try:
            text += str(i+1) + '.〖' + listTuple_user_name_and_num[i][0] + "〗→「" + str(
                listTuple_user_name_and_num[i][1][0]) + '」\n'
        except Exception:
            text += str(i+1) + '.〖' + listTuple_user_ojName_and_num[i][0] + "〗→「" + str(
                listTuple_user_ojName_and_num[i][1][0]) + '」\n'
    text += "比赛题单刷新时间:\n" + \
        time.strftime('%m-%d %H:%M:%S',
                      time.localtime(data_goodmoring['race_time'])) + '\n'
    text += "耗时:" + str(round(time.time() - start_time, 2)) + '秒'

    if not isGetTodayRank:
        # 发送榜单并记录消息id
        msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=text, auto_escape=False))['message_id']
        # 自动撤回上一条榜单
        dict_msg_id.update({time.time(): {event.group_id: msg_id}})
    else:
        isGetTodayRank = False
        return listTuple_user_ojName_and_num


# 从网站获取数据
async def url_to_soup(url):
    async with AsyncClient() as client:
        response = await client.get(url)
        return BeautifulSoup(response.text, 'html.parser')


@get_today_rank.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    time_now = time.time()
    isRefresh = event.get_message().extract_plain_text()[0:2] == '刷新'
    global isGetTodayRank
    isGetTodayRank = True
    listTuple_user_name_and_num_new = await _get_rank(bot, event)
    rank_length = 0
    for ele in listTuple_user_name_and_num_new:
        rank_length += 1
    # 判断是否需要刷新
    if isRefresh:
        # 刷新榜单
        await refresh_ranking(rank_length, listTuple_user_name_and_num_new, time_now)
        text = await get_first(bot, rank_length, listTuple_user_name_and_num_new, time_now)
        msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=text))['message_id']
        dict_msg_id.update({time_now: {event.group_id: msg_id}})
        return
    # 获取新旧榜单差值, 得到今日题数
    listTuple_difference = await get_difference(bot, event.group_id, rank_length, listTuple_user_name_and_num_new)
    text = '  今日卷王天梯榜(前20)\n'
    rank = ''
    for i in range(rank_max_length):
        if listTuple_difference[i][1] == 0:
            break
        if listTuple_difference[i][0] == 'time':
            continue
        rank += str(i+1) + '.〖' + \
            listTuple_difference[i][0] + '〗→「' + \
            str(listTuple_difference[i][1]) + '」\n'
    if rank == '':
        rank += '......今天榜上无人呢(ﾟ⊿ﾟ)ﾂ......\n'
    text += rank
    text += "比赛题单刷新时间:\n" + \
        time.strftime('%m-%d %H:%M:%S',
                      time.localtime(data_goodmoring['race_time'])) + '\n'
    text += "清零时间:" + \
        time.strftime('%m-%d %H:%M:%S',
                      time.localtime(data_today_rank['time'])) + '\n'
    text += "耗时: " + str(round(time.time() - time_now, 2)) + '秒'

    # 发送榜单并记录消息id
    msg_id = (await bot.send_msg(message_type='group', group_id=event.group_id, message=text, auto_escape=False))['message_id']
    dict_msg_id.update({time.time(): {event.group_id: msg_id}})


# 定时刷新榜单
async def timing_refresh_ranking(bot: Bot, time_now):
    global isRefreshing
    if isRefreshing:
        return
    isRefreshing = True  # 标记当前状态, 防止重复发送
    listTuple_user_ojName_and_num = await get_ojName_and_id(time_now)
    rank_length = 0
    for ele in listTuple_user_ojName_and_num:
        rank_length += 1
    text = await get_first(bot, rank_length, listTuple_user_ojName_and_num, time_now)
    # 更新榜单
    await refresh_ranking(rank_length, listTuple_user_ojName_and_num, time_now)
    isRefreshing = False
    await bot.send_msg(message_type='group', group_id=535768255, message=text, auto_escape=False)


# 将新旧榜单做差, 获取今日题数
async def get_difference(
    bot,
    group_id,
    rank_length,
    listTuple_user_name_and_num_new,
):
    dict_difference = {}
    for i in range(rank_length):  # 遍历新榜单
        bool_finded = False  # 是否在旧榜单找到新榜单的标记
        for ele_old in data_today_rank:  # 遍历旧榜单的用户id
            # 当遍历到相同的key, 将value相减并添加进输出的字典
            if listTuple_user_name_and_num_new[i][0] == ele_old:
                bool_finded = True  # 找到
                # 尝试获取用户的群名片
                # 若用户id不为数字则不是qq号
                if listTuple_user_name_and_num_new[i][1][1] == 'none':
                    dict_difference.update(
                        {listTuple_user_name_and_num_new[i][0]: listTuple_user_name_and_num_new[i][1][0] - data_today_rank[ele_old]})
                else:
                    try:
                        user_info = await bot.get_group_member_info(group_id=group_id, user_id=int(listTuple_user_name_and_num_new[i][1][1]), no_cache=False)
                        if len(user_info['card']):
                            dict_difference.update(
                                {user_info['card']: listTuple_user_name_and_num_new[i][1][0] - data_today_rank[ele_old]})
                        elif len(user_info['nickname']):
                            dict_difference.update(
                                {user_info['nickname']: listTuple_user_name_and_num_new[i][1][0] - data_today_rank[ele_old]})
                        else:
                            dict_difference.update(
                                {listTuple_user_name_and_num_new[i][0] + '(' + listTuple_user_name_and_num_new[i][1][1] + ')': listTuple_user_name_and_num_new[i][1][0] - data_today_rank[ele_old]})
                    # 若报错则说明用户不在群内
                    except Exception:
                        # 若用户id为数字则为qq号, 将qq号放在后面
                        dict_difference.update(
                            {listTuple_user_name_and_num_new[i][0] + '(' + listTuple_user_name_and_num_new[i][1][1] + ')': listTuple_user_name_and_num_new[i][1][0] - data_today_rank[ele_old]})

        # 若在旧榜单没有找到, 则直接添加进差值
        if not bool_finded:
            # 尝试获取用户的群名片
            try:
                user_info = await bot.get_group_member_info(group_id=group_id, user_id=int(listTuple_user_name_and_num_new[i][1][1]), no_cache=False)
                dict_difference.update(
                    {user_info['card'] or user_info['nickname']: listTuple_user_name_and_num_new[i][1][0]})
            # 若报错则说明用户不在群内
            except Exception:
                # 若用户id为数字则为qq号, 将qq号放在后面
                if listTuple_user_name_and_num_new[i][1][1] != 'none':
                    dict_difference.update(
                        {listTuple_user_name_and_num_new[i][0] + '(' + listTuple_user_name_and_num_new[i][1][1] + ')': listTuple_user_name_and_num_new[i][1][0]})
                    # 若用户id不为数字则不是qq号
                else:
                    dict_difference.update(
                        {listTuple_user_name_and_num_new[i][0]: listTuple_user_name_and_num_new[i][1][0]})
    # 对输出字典进行排序
    listTuple_difference = sorted(
        dict_difference.items(), key=lambda x: x[1], reverse=True)
    return listTuple_difference


# 计算昨日卷王
async def get_first(
    bot: Bot,
    rank_length,
    listTuple_user_ojName_and_num,
    time_now
):
    listTuple_difference = await get_difference(bot, 535768255, rank_length, listTuple_user_ojName_and_num)
    text = '    【每日卷王天梯榜清算】\n'
    if rank_length > 0:
        text += ' 恭喜 ' + listTuple_difference[0][0] + ' 成为昨日卷王!\n'
    text += '昨日排行:\n'
    rank = ''
    for i in range(rank_length):
        if listTuple_difference[i][1] == 0:
            break
        if listTuple_difference[i][0] == 'time':
            continue
        rank += str(i+1) + '.〖' + \
            listTuple_difference[i][0] + '〗→「' + \
            str(listTuple_difference[i][1]) + '」\n'
    if rank == '':
        rank += '......昨天榜上没有卷王呢( ´ﾟωﾟ)？......\n'
    text += rank
    text += "耗时:" + str(round(time.time() - time_now, 2)) + '秒'
    return text


# 刷新榜单
async def refresh_ranking(
        rank_length,
        listTuple_user_name_and_num_new,
        time_now):
    with open(FILE_TODAY_RANK, 'w', encoding='utf-8') as file:
        for i in range(rank_length):
            data_today_rank.update(
                {listTuple_user_name_and_num_new[i][0]: listTuple_user_name_and_num_new[i][1][0]})
        data_today_rank['time'] = time_now  # 更新时间
        file.write(json.dumps(data_today_rank, ensure_ascii=False))
        file.close()


# 单独获取oj用户名及id
async def get_ojName_and_id(time_now: float):
    url = 'https://oj.fjnuacm.top/d/junior/ranking'
    try:
        soup = await url_to_soup(url)
        if soup.select('a.pager__item.next.link'):
            soup = await get_next_soup(soup)
    except Exception as e:
        await get_today_rank.finish(repr(e))
    user_name = soup.select('a.user-profile-name')   # 获取用户名
    user_id = soup.select('img.small')  # 获取带有用户id
    num = soup.select('td.col--ac')  # 获取ac题数Tag
    list_user_ojName = []  # 用户名
    list_user_id = []   # qq号
    dict_user_ojName_and_num = {}
    rank_length = 0
    # 将用户名中的空格和换行符去除
    for ele in user_name:
        string = str(user_name[rank_length].string).strip()
        list_user_ojName.append(string)
        rank_length += 1
    # 获取qq号
    for i in range(rank_length):
        find_text = re.compile(r'\d+').findall(user_id[i].attrs['src'])
        if len(find_text) == 3 and find_text[2] == '160':
            list_user_id.append(find_text[1])
        else:
            list_user_id.append('none')

    # 获取题数Tag中的题数
    for i in range(rank_length):
        ele = num[i].string
        dict_user_ojName_and_num.update(
            {list_user_ojName[i]: [int(ele), list_user_id[i]]})  # type:ignore
    # 根据题数从小到大排序用户
    listTuple_user_ojName_and_num = sorted(
        dict_user_ojName_and_num.items(), key=lambda x: x[1], reverse=True)
    return listTuple_user_ojName_and_num


# 定时刷新比赛题单时间
async def timing_refresh_race_time(bot: Bot):
    driver = webdriver.Firefox()
    time_now = time.time()
    try:
        driver.get('https://oj.fjnuacm.top/d/junior/login/')
        # 输入用户名
        driver.find_element(
            By.XPATH, "/html/body/div[2]/div[4]/div/div/div/form/div[1]/div/label/input").send_keys('yuns')
        # 输入密码
        driver.find_element(
            By.XPATH, "/html/body/div[2]/div[4]/div/div/div/form/div[2]/div/label/input").send_keys('sensen')
        # 登录
        element = driver.find_element(
            By.XPATH, "/html/body/div[2]/div[4]/div/div/div/form/div[5]/div/div/input[2]")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(10)
        # 打开控制面板
        element = driver.find_element(
            By.XPATH, "/html/body/nav[1]/div/div/ol[1]/li[11]/a")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(10)
        # 打开脚本管理
        element = driver.find_element(
            By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/div/div/ol/li/ol/li[2]/a")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(5)
        # 打开脚本
        element = driver.find_element(
            By.XPATH, "/html/body/div[2]/div[3]/div/div[1]/div[2]/div[2]/div/table[2]/tbody/tr[2]/td[3]/a")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(3)
        # 运行脚本
        element = driver.find_element(
            By.XPATH, "/html/body/div[4]/div/div[2]/div/div/button[2]")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(11)
        driver.close()
        with open(FILE_GOODMORNING, 'w') as file:
            data_goodmoring['race_time'] = time_now
            json.dump(data_goodmoring, file)
            file.close()
    except:
        driver.close()
        with open(FILE_GOODMORNING, 'w') as file:
            data_goodmoring['race_time'] = time_now
            json.dump(data_goodmoring, file)
            file.close()
