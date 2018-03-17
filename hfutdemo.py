# -*- coding: utf-8 -*-
import os
import re
import urllib.request, urllib.error, urllib.parse
import sys
import pymysql
import imp

imp.reload(sys)
# sys.setdefaultencoding('utf8')

# 打开数据库连接
db = pymysql.connect(
        host='localhost',
        port=3307,
        user='root',
        password='',
        db='news',
    )

# 使用cursor()方法获取操作游标
cursor = db.cursor()


# 得到页面全部内容
def askURL(url):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    try:
        request = urllib.request.Request(url, headers=headers)  # 发送请求
        response = urllib.request.urlopen(request)  # 取得响应
        html = response.read().decode()  # 获取网页内容
        # print html
        # html = html.encode('utf-8', 'ignore')    # 将unicode编码转为utf-8编码
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
            html = ""
        if hasattr(e, "reason"):
            print(e.reason)
            html = ""
    return html


# 得到正文
def getContent(url):
    html = askURL(url)
    if (html != ""):
        newsContent = ''
        output = {'title': '', 'date': '', 'writer': '', 'photoer': '', 'editor': '', 'newsContent': ''}
        # 找到新闻标题
        title = re.compile(r'<h2>'r'(.*)<br />')
        titleList = re.findall(title, html)
        if (titleList > 0):
            output['title'] = titleList[0]
        # 找到新闻发布日期
        date = re.compile(r'<span class="t">发布日期：'r'(.*)&nbsp;&nbsp;字号：')
        output['date'] = re.findall(date, html)[0]
        # 找到新闻作者
        writer = re.compile(r'（'r'(.*)/文')
        writerList = re.findall(writer, html)
        if (len(writerList) > 0):
            output['writer'] = writerList[0]
        # 拍照作者
        photoer = re.compile(r'&nbsp;&nbsp;'r'(.*)/图）')
        photoerList = re.findall(photoer, html)
        if (len(photoerList) > 0):
            output['photoer'] = photoerList[0]
        # 文章编辑
        editor = re.compile(r'编辑：'r'(.*)</div>')
        editorList = re.findall(editor, html)
        # print 'editor大小='+editorList
        if (len(editorList) > 0):
            output['editor'] = editorList[0]
        # 找到新闻主体所在的标签
        findDiv = re.compile(r'<div id="artibody" class="content f16">'
                             r'(.*)<div style=" text-align:right;">', re.S)
        div = re.findall(findDiv, html)
        if len(div) != 0:
            content = div[0]
            # print content
            newsContent = re.sub(r'<p.*?>', '', content)  # 去掉段落开头的<p>标签
            if newsContent.find('<img') > 0:
                newsContent = re.sub(r'<img.*?src="', '', newsContent)
                newsContent = re.sub(r'jpg".*?/>', 'jpg', newsContent)
                newsContent = re.sub(r'</p>', '\n', newsContent)  # 取出掉段落末尾的</p>标签
            labels = re.compile(r'<.*?>', re.S)  # 去除文章中的标签
            newsContent = re.sub(labels, '', newsContent)
            newsContent = re.sub(r'&nbsp;', '', newsContent)
            # print newsContent
            output['newsContent'] = newsContent
        return output
    return ""


# 根据类别按顺序命名文件
def saveFile(labelName, date, fileNum):
    dirname = "news"
    # 若目录不存在，就新建
    if (not os.path.exists(dirname)):
        os.mkdir(dirname)
    labelName1 = labelName.encode('gbk', 'ignore')
    labelpath = dirname + '\\' + labelName1
    if (not os.path.exists(labelpath)):
        os.mkdir(labelpath)
    path = labelpath + "\\" + date + "-0" + str(fileNum) + ".txt"  # w文本保存路径
    printPath = dirname + "\\" + labelName.encode('utf-8', 'ignore') + "\\" + date + "-0" + str(
        fileNum) + ".txt"  # w文本保存路径
    print("正在下载" + printPath)
    # path=path.encode('gbk','utf-8')#转换编码
    f = open(path, 'w+')
    return f


# 保存数据到数据库
# SQL 插入语句
def insertData(date, title, content, writer, photoer, editor, url):
    sql = """INSERT INTO mainNews(date, title, content, writer, photoer, editor, url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    print('准备插入数据')
    try:
        # 执行sql语句
        cursor.execute(sql, (date, title, content, writer, photoer, editor, url))
        # 提交到数据库执行
        db.commit()
        print('插入成功')

    except:  # Rollback in case there is any error
        print('插入失败')
        db.rollback()  # 关闭数据库连接


# 得到正文的URL，读取正文，并保存
def getURL(nurl):
    text = ''
    html = askURL(nurl)
    # print html
    findDiv = re.compile(r'<li><span class="rt">(.*?)  target="_blank" style="" >', re.S)
    findTime = re.compile(r'(.*)</span>')
    findTitle = re.compile(r'title="(.*)"')
    findURL = re.compile(r'<a href="(.*)" title')
    # findLabel = re.compile(r'<h3.*?</span>(.*?)</h3>')
    # fileNum = 0
    # list = re.findall(findDiv, html)
    # print list[0]x
    # labelName = re.findall(findLabel, html)[0]
    for info in re.findall(findDiv, html):
        # print info
        time = re.findall(findTime, info)[0]
        # print time
        title = re.findall(findTitle, info)[0]
        url = re.findall(findURL, info)[0]  # 获取新闻正文的链接
        url = 'http://news.hfut.edu.cn' + url
        print(time + ' ' + title + ' ' + url)
        try:
            text = getContent(url)
            insertData(text['date'], text['title'], text['newsContent'], text['writer'], text['photoer'],
                       text['editor'], url)
            # text = {'title': '', 'date': '', 'writer': '', 'photoer': '', 'editor': '', 'newsContent': ''}
        except urllib.error.URLError as e:
            if hasattr(e, "reason"):
                print("抓取错误" + url, e.reason)
        except Exception as e:
            print("抓取错误" + url, e)
        # print labelName + '...' + text['date'], text['title'], text['newsContent'], text['writer'], text['photoer'],text['editor']
        # 如果新闻内容长度大于100，保存新闻标题和正文
        # fileNum = fileNum + 1
        # f = saveFile(labelName, time, fileNum)
        # f.write(text)
        # f.close()  # 抓取新闻标题、类别、发布时间、url，并建立相应的文件，存到相应的类别文件夹中


def getNews(url, begin_page, end_page):
    for i in range(begin_page, end_page + 1):
        nurl = url + str(i) + ".html"
        print('----------开始打印第' + str(i) + '页---------------')
        # 获取网页内容
        getURL(nurl)
    db.close()


# 接收输入类别、起始页数、终止页数
def main():
    url = 'http://news.hfut.edu.cn/list-1-'
    begin_page = int(input('请输入开始的页数(1,)：\n'))
    end_page = int(input('请输入终点的页数(1,)：\n'))
    getNews(url, begin_page, end_page)
    # getNews(url, 1, 2)


main()

