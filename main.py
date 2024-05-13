import requests
import json
import os


header = {
    'Cookie': 'Secure; JSESSIONID=3F0E25BAD7B4818F4E468AF3E519892C; Secure; SF_cookie_3=26141024; Secure'
}


def query(page):
    data = f"xnm=&xqm=&_search=false&nd=&queryModel.showCount=15&queryModel.currentPage={page}&queryModel.sortName=&queryModel.sortOrder=asc&time="
    url = f"https://jwglxt.fjnu.edu.cn/jwglxt/cjcx/cjcx_cxXsgrcj.html?doType=query&gnmkdm=N305005&su=121052021038&{data}"
    res = requests.post(url=url, headers=header)
    res = json.loads(res.text)
    res = res['items']
    if len(res) > 0:
        str = ''
        for ele in res:
            str += ele['kcmc'] + " " + ele['cj'] + '\n'
        return str
    else:
        return 0


if __name__ == "__main__":
    page = 1
    output = ''
    while 1:
        str = query(page)
        if not str:
            break
        else:
            output += str
        page += 1
    if output:
        os.startfile("run.bat")
