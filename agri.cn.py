# -*- coding: utf-8 -*-
# shanjixiaboss

import os
import re
import urllib.request, urllib.error, urllib.parse
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
        nurl = url + str(i) + ".htm"
        print('----------开始打印第' + str(i) + '页---------------')
        # 获取网页内容
        getURL(nurl)
    db.close()


# 得到正文的URL，读取正文，并保存
def getURL(nurl):
    text = ''
    html = getBody(nurl)
    soup = BeautifulSoup(html, 'html.parser')
    findDiv = soup.find("div", class_="lb_m1")
    findLi = findDiv.find_all_next("li", limit= 15)

    for info in findLi:

        title = info.find('title')
        time = str(info.find('span').get_text()).replace('(', '').replace(')', '')

        url = info.find('a').get('href')
        fileName = str(url).split('/')[2].replace('.htm', '')

        url = 'http://www.agri.cn/province/jiangsu/tzgg' + url.replace('./', '/')

        try:
            text = getContent(url, fileName)
            # print(text)
            insertData(text['title'], text['content_path'], url, time)

        except Exception as e:
            print("抓取错误" + url, e)

        f = saveFile(fileName) # 时间格式文件
        f.write(text['newsContent'].encode())
        f.close()


# 得到页面全部内容
def getBody(url):
    # 请求头
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}

    try:
        request = urllib.request.Request(url, headers=headers)  # 发送请求
        response = urllib.request.urlopen(request)  # 取得响应
        html = response.read().decode()  # 获取网页内容
        # html = html.encode('utf-8', 'ignore')    # 将unicode编码转为utf-8编码

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
        output = {'title': '', 'newsContent': '', 'content_path': ''}
        # 找到新闻标题
        title = soup.find('div', class_='nr_m14').get_text()
        output['title'] = title

        # 新闻内容
        newsContent = soup.find(id="TRS_AUTOADD")
        if (newsContent != ""):
            output['newsContent'] = newsContent
            output['content_path'] = 'article' + fileName + ".json"

        return output
    return ""


# 根据类别按顺序命名文件
def saveFile(date):
    dirname = "article"
    # 若目录不存在，就新建
    if (not os.path.exists(dirname)):
        os.mkdir(dirname)

    path = dirname + "\\" + 'article' + str(date) + ".json"  # w文本保存路径
    printPath = 'article' + str(date) + ".json"  # w文本保存路径
    # print("正在下载" + printPath)
    # path=path.encode('gbk','utf-8')#转换编码
    f = open(printPath, 'wb')
    return f


# 保存数据到数据库
# SQL 插入语句
def insertData(title, content_path, url, time):

    sql = "INSERT INTO v1_article_draft(title, admin_uid, author, type, `from`, content_path, link_url, video_url, tag, tags, create_time, update_time) VALUES ('%s', 2, '中国农业信息网', 1, 1, '%s', '%s', '', '', '', '%s', '2017-11-06 14:57:17')" % (title, content_path, url, time)

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
    url = 'http://www.agri.cn/province/jiangsu/tzgg/index_'
    begin_page = int(input('请输入开始的页数(1,)：\n'))
    end_page = int(input('请输入终点的页数(1,)：\n'))
    getNews(url, begin_page, end_page)
    # getNews('http://www.agri.cn/province/jiangsu/nyyw/index')


main()

