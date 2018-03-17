# -*- coding: utf-8 -*-
# shanjixiaboss
# 2017-11-09 11:06:28

import os
import re
import urllib.request, urllib.error, urllib.parse
import json
import string
import pymysql
from bs4 import BeautifulSoup
import datetime


# 打开数据库连接
db = pymysql.connect(
        host='',
        port=,
        user='',
        password='',
        db='',
        charset='utf8'
    )

# 使用cursor()方法获取操作游标
cursor = db.cursor()


# 获取列表
def getNews(url, begin_page, end_page):
    for i in range(begin_page, end_page + 1):
        nurl = url + str(i)
        print('----------开始打印第' + str(i) + '页---------------')
        # 获取网页内容
        getURL(nurl)
    db.close()


# 得到正文的URL，读取正文，并保存
def getURL(nurl):
    text = ''
    url = ''
    html = getBody(nurl)
    soup = BeautifulSoup(html, 'html.parser')

    listData = soup.select('table[width="98%"]')

    for info in listData:

        time = info.select('td[align="right"]')[0].get_text() # 时间
        url = 'http://www.ofdc.org.cn/' + info.find('a').get('href') # 链接地址

        fileName = str(url).split('n_id=')[1] # 存放文件名

        # thumb = info.find('img').get('src') # 缩略图
        thumb = ''

        try:
            text = getContent(url, fileName)
            print(text)
            insertData(text['title'], text['content_path'], text['mongo_id'],  url, time, thumb)

        except Exception as e:
            print("抓取错误" + url, e)

        # f = saveFile(fileName) # 时间格式文件
        # f.write(text['newsContent'].encode())
        # print("写入成功")
        # f.close()


# 得到页面全部内容
def getBody(url):
    # 请求头
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}

    try:
        request = urllib.request.Request(url, headers=headers)  # 发送请求
        response = urllib.request.urlopen(request)  # 取得响应
        html = response.read().decode('gb2312')  # 获取网页内容 将unicode编码转为utf-8编码

    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
            html = ""
        if hasattr(e, "reason"):
            print(e.reason)
            html = ""
    return html


# 筛选字段
def getContent(url, fileName):
    html = getBody(url)

    if (html != ""):
        soup = BeautifulSoup(html, 'html.parser')
        content_path = ''
        output = {'title': '', 'newsContent': '', 'content_path': '', 'mongo_id': ''}
        # 找到新闻标题
        title = soup.find('h3').get_text()
        output['title'] = title

        # 新闻内容
        newsContent = soup.find(class_="zclass1")

        if (newsContent != ""):
            output['newsContent'] = newsContent
            # output['content_path'] = 'public/uploads/article/draft/article' + fileName + ".json"
            output['content_path'] = ''

            output['mongo_id'] = postContent(newsContent)
            # print(output)

        return output
    return ""


# 根据类别按顺序命名文件
def saveFile(date):
    dirname = "article"
    # 若目录不存在，就新建
    if (not os.path.exists(dirname)):
        os.mkdir(dirname)

    # path = dirname + "\\" + 'article' + str(date) + ".json"  # w文本保存路径
    printPath = 'article' + str(date) + ".json"  # w文本保存路径
    # print("正在下载" + printPath)
    # path=path.encode('gbk','utf-8')#转换编码
    f = open(printPath, 'wb')
    return f

def postContent (content):
    # 请求头
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}

    try:
        # url = 'http://wzbtest.ecoprobio.cn/v1/file/upload?params=' + '{"content":' +  content + '}'
        # print(url)
        # params = urllib.parse.quote(url, safe=string.printable)
        params = urllib.parse.quote(str(content).replace('%22', '%27'))
        # print(params)
        # request = urllib.request.Request('http://192.168.1.4:8020/v1/file/upload?params={%22content%22:%2224234234234%22}')  # 发送请求

        params = urllib.parse.urlencode({'content': content})

        response = urllib.request.urlopen("http://wzbtest.ecoprobio.cn/v1/file/upload?params={'content': "+ params + "}")   # 取得响应

        result = response.read().decode('UTF-8')
        # result = ''
        result = json.loads(result)['data']
        # print(result)

    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return result


# 保存数据到数据库
# SQL 插入语句
def insertData(title, content_path, mongo_id, url, time, thumb):

    sql = "INSERT INTO v1_article_draft(title, admin_uid, author, type, `from`, content_path, mongo_id, link_url, cover_url, video_url, tag, tags, create_time, update_time) VALUES ('%s', 2, '农卖网', 1, 1, '%s', '%s', '%s', '%s', '', '', '', '%s', '%s')" % (title, content_path, mongo_id, url, thumb, time, datetime.datetime.now())

    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        print('插入成功')

    except Exception as e:
        print('失败原因' + e)
        db.rollback()  # 关闭数据库连接


# 接收输入类别、起始页数、终止页数
def main():
    url = 'http://www.ofdc.org.cn/article.asp?c_id=3&page='
    # begin_page = int(input('请输入开始的页数(1,)：\n'))
    # end_page = int(input('请输入终点的页数(1,)：\n'))
    # getNews(url, begin_page, end_page)

    getNews(url, 1, 1)
main()

