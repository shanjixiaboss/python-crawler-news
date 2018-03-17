#!/user/bin/python
#-*- coding:utf-8 -*-

from urllib import parse,request
import json


header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}

url = 'http://wzbtest.ecoprobio.cn/v1/file/upload?params='

req = request.Request(url=url,data=parse.urlencode({"params":{"content": "admin"}}).encode(encoding='utf-8'))

# res = request.urlopen(url + json.dumps({"content":"1111"}))

res = request.urlopen(req)

res = res.read()

b = json.loads(res)

print(b["data"])
print(res)
#输出内容:b'{"result":"error","msg":"\xe5\x8f\x82\xe6\x95\xb0\xe6\xa0\xbc\xe5\xbc\x8f\xe4\xb8\x8d\xe6\xad\xa3\xe7\xa1\xae","code":"10000002","data":"10000002"}'
print(res.decode(encoding='utf-8'))
#输出内容:{"result":"error","msg":"参数格式不正确","code":"10000002","data":"10000002"}













# #!/user/bin/python
# #-*- coding:utf-8 -*-
#
# from urllib import parse,request
# import json
#
#
# textmod={"content":"admin"}
# #json串数据使用
# print(textmod)
#
# textmod = json.dumps(textmod).encode(encoding='utf-8')
# print(textmod)
# #普通数据使用
# # textmod = parse.urlencode(textmod).encode(encoding='utf-8')
# print(textmod)
# #输出内容:b'{"params": {"user": "admin", "password": "zabbix"}, "auth": null, "method": "user.login", "jsonrpc": "2.0", "id": 1}'
# header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
# url = 'http://wzbtest.ecoprobio.cn/v1/file/upload'
# req = request.Request(url=url,data=parse.urlencode({params:{"content": "admin"}}).encode(encoding='utf-8'))
# res = request.urlopen(req)
# res = res.read()
# print(res)
# #输出内容:b'{"jsonrpc":"2.0","result":"37d991fd583e91a0cfae6142d8d59d7e","id":1}'
# print(res.decode(encoding='utf-8'))
# #输出内容:{"jsonrpc":"2.0","result":"37d991fd583e91a0cfae6142d8d59d7e","id":1}