'''
Version:1.0
Author:Zacama
Date:2019.09.26
注：1.使用此脚本，需将后缀名为.torrent类型的文件默认打开方式设置为utorrent，
    且utorrent设置为不弹窗，直接下载，否则会出现未知问题。
    2.此脚本启动后，一小时自动执行一次(可自行更改频率)，除非人工关闭。
    3.脚本启动后，会在当前路径下生成一个cookies.txt文件
    4.此脚本仅限六维空间使用(bt.neu6.edu.cn)
'''
import requests, os, re, time
import http.cookiejar as cookielib
from bs4 import BeautifulSoup

session = requests.session()
new_cookie_jar = cookielib.LWPCookieJar('cookie.txt')


def get_cookie():
    load_cookiejar = cookielib.LWPCookieJar()
    load_cookiejar.load('cookies.txt', ignore_discard=True, ignore_expires=True)
    load_cookies = requests.utils.dict_from_cookiejar(load_cookiejar)
    session.cookies = requests.utils.cookiejar_from_dict(load_cookies)
    return session.cookies


def isLoginStatus():
    route_url = "http://bt.neu6.edu.cn/plugin.php?id=neubt_resourceindex"
    response_res = requests.get(route_url, cookies=get_cookie(), allow_redirects=False)
    return False if response_res.status_code != 200 else True


def login(username, password):
    print('The cookie has been lost or has expired.\nAccount has been re-logged in.\nCookie has been updated.')
    url = 'http://bt.neu6.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=Lavei&inajax=1'
    data = {
        'username': username,
        'password': password,
    }
    headers = {'Host': 'bt.neu6.edu.cn', 'Connection': 'keep-alive', 'Content-Length': '151',
               'Cache-Control': 'max-age=0', 'Origin': 'http://bt.neu6.edu.cn', 'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36',
               'Content-Type': 'application/x-www-form-urlencoded', 'DNT': '1',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'Referer': 'http://bt.neu6.edu.cn/member.php?mod=logging&action=login&referer=http%3A%2F%2Fbt.neu6.edu.cn%2Fforum.php',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
               }
    session.headers.clear()
    session.headers.update(headers)
    r = session.post(url, data)
    requests.utils.cookiejar_from_dict({c.name: c.value for c in session.cookies}, new_cookie_jar)
    new_cookie_jar.save('cookies.txt', ignore_discard=True, ignore_expires=True)


def extract_link(html_file):
    soup = BeautifulSoup(html_file, 'html.parser')
    link_list = ['http://bt.neu6.edu.cn/' + str(x)[23:46] for x in soup.find_all(href=re.compile('^t'))][0:5]
    # 更改':'后面的数字，可以决定索引前N个torrent
    return link_list


def extract_torrent_name(torrent_page_link_list):
    torrent_list = []
    for link in torrent_page_link_list:
        link_page = requests.get(link, cookies=get_cookie())

        name_rule_text = r'id="aid\d+" target="_blank">(.*?)</a>'
        name_rule = re.compile(name_rule_text, re.S)
        false_name_list = re.findall(name_rule, link_page.text)

        link_rule_text = r'(aid=\w+)"'
        link_rule = re.compile(link_rule_text, re.S)
        link_list = re.findall(link_rule, link_page.text)[0]

        name_list = [name for name in false_name_list if 'torrent' in name]
        for name in name_list:
            if 'torrent' in name:
                name = '[neubt]' + name
                real_link = 'http://bt.neu6.edu.cn/forum.php?mod=attachment&' + link_list
                torrent_list.append([name, real_link])
    return torrent_list


def check_new_torrent(torrent_list):
    filename_list = [name for name in os.listdir('x:/x')]  # 这里是torrent文件的保存路径，与下面两个路径保持一致，根据自己电脑的情况自行修改保存路径
    new_torrent_list = []
    for index, torrent in enumerate(torrent_list):
        if torrent[0] not in filename_list:
            new_torrent_list.append(torrent)
    return new_torrent_list


def get_download_url(final_torrent_list):
    for torrent in final_torrent_list:
        url = torrent[1]
        req = requests.get(url, cookies=get_cookie())
        req_rule_text = r'btnleft"><a href="(.*?)"'
        req_rule = re.compile(req_rule_text, re.S)
        try:
            real_req = re.findall(req_rule, req.text)[0]
            real_link = 'http://bt.neu6.edu.cn/' + real_req
        except IndexError:
            real_link = url

        torrent[1] = real_link
    return final_torrent_list


# 下载完新的torrent，直接使用utorrent下载
def download_torrent(real_torrent_list):
    for torrent in real_torrent_list:
        file = requests.get(torrent[1], cookies=get_cookie())  # 根据自己电脑的情况自行修改保存路径
        with open('x:/x/' + torrent[0], 'wb') as f:  # 下面这两个路径最后面要多加一个'/',因为后面要接文件名
            f.write(file.content)
        os.startfile('x:/x/' + torrent[0])  # 这里是torrent文件的保存路径与上面两个路径保持一致，根据自己电脑的情况自行修改保存路径


if __name__ == '__main__':
    check_times = 0
    while 1:
        files = [x for x in os.listdir('./')]
        if 'cookies.txt' in files and os.path.getsize('cookies.txt') != 0 and isLoginStatus() is True:
            pass  # print('The old cookie is still useful.')
        else:
            login('ID', 'password')  # 次数输入六维空间账号ID和密码，账号ID可在个人资料中找到
        response = requests.get('http://bt.neu6.edu.cn/plugin.php?id=neubt_resourceindex', cookies=get_cookie())
        torrent_page_link_list = extract_link(response.text)
        torrent_list = extract_torrent_name(torrent_page_link_list)
        final_torrent_list = check_new_torrent(torrent_list)
        real_torrent_list = get_download_url(final_torrent_list)
        download_torrent(real_torrent_list)
        check_times += 1
        print('The program has run %s times.' % check_times)
        time.sleep(3600)  # 单位是秒
