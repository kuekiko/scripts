import hashlib
import requests
import time
import json
import secrets
import string


# 登陆获取COOKIE
def login(account, password):
    url = 'https://user.allcpp.cn/api/login/normal'
    data = {
        'account': account,
        'password': password,
        'phoneAccountBindToken': 'undefined',
        'thirdAccountBindToken': 'undefined'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Origin': 'https://cp.allcpp.cn',
        'Referer': 'https://cp.allcpp.cn/'
    }
    response = requests.post(url, data=data, headers=headers)
    response_obj = json.loads(response.text)
    if t := response_obj.get('token'):
        print(f"token={t}")
        return t
    else:
        return ""

# 获取购票人信息
def get_purchaser(token):
    url = "https://www.allcpp.cn/allcpp/user/purchaser/getList.do"
    headers = {
        "Host": "www.allcpp.cn",
        "Cookie": f"token={token};",
        "Sec-Ch-Ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        "Accept": "application/json, text/plain, */*",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://cp.allcpp.cn",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://cp.allcpp.cn/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }
    ids = []
    response = requests.get(url, headers=headers)
    info = response.json()
    if len(info) != 0:
        for i in info:
            ids.append(str(i['id']))
            print(f"购票人信息info->{i}")
        return ids
    else:
        return []

## 获取票的类别
def get_TicketType(token,eventMainId):
    url = f"https://www.allcpp.cn/allcpp/ticket/getTicketTypeList.do?eventMainId={eventMainId}"
    headers = {
        "Host": "www.allcpp.cn",
        "Cookie": f"token={token};",
        "Sec-Ch-Ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        "Accept": "application/json, text/plain, */*",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://cp.allcpp.cn",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://cp.allcpp.cn/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
    }

    response = requests.get(url, headers=headers)
    resText = response.json()
    if info:=resText.get("ticketTypeList"):
        return info
    else:
        return []

# 尝试提交订单  这里是支付宝购买 可能有bug  看到成功字样后 自己手动往个人订单里面
def commit(token, ticket_type_id, count, purchaser_ids,rtime=30):
    base_url = "https://www.allcpp.cn/allcpp/ticket/buyTicketAlipay.do"
    # # 定义请求头
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Content-Length": "2",
        "Content-Type": "application/json;charset=UTF-8",
        "Cookie": f"token={token};",
        "Host": "www.allcpp.cn",
        "Origin": "https://cp.allcpp.cn",
        "Referer": "https://cp.allcpp.cn/",
        "Sec-Ch-Ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"
    }

    while True:
    # 拼接完整URL
        try:
            timestamp = str(int(time.time())) ##"1682074579"
            ## 貌似并不校验 sign: a()(t + r + i + e + n)
            # nonce="jcFFFK4pPz2eNGBND3xDxTEyZ7PGCyzm" ## 32位随机值即可
            n = string.ascii_letters + string.digits
            nonce = ''.join(secrets.choice(n) for i in range(32))
            sign=hashlib.md5(f"2x052A0A1u222{timestamp}{nonce}{ticket_type_id}2sFRs".encode('utf-8')).hexdigest()
            # print(f"ticket_type_id={ticket_type_id}")
            # print(f"nonce={nonce}")
            # print(f"timestamp={timestamp}")
            # print(f"sign={sign}")
            url = f"{base_url}?ticketTypeId={ticket_type_id}&count={count}&nonce={nonce}&timeStamp={timestamp}&sign={sign}&purchaserIds={purchaser_ids}"
            response = requests.post(url, json={},timeout=30,headers=headers)
            if response.status_code!=200:
                ## 应该就是失败
                print("请求抢票失败")
                print(response.text)
            else:
                # print(response.text)
                res = response.json()
                if res.get('isSuccess'):
                    print("抢票成功")
                else:
                    print("抢票失败")
                    print(response.text)
            time.sleep(rtime)
        except Exception as e:
            print(f"发生异常: {e}")
            time.sleep(rtime)

# 需要的信息 发给别人记得清空 嫌麻烦就手动填上不用每次输入
account = ""
password = ""
## 手动输入
if account=="":
    account = input("请输入登陆号：")
if password=="":
    password = input("请输入登陆密码：")

token = login(account, password)

TicketType = get_TicketType(token,1074) ## 1074 为cp29 可能会变动？yes则及时修改
if len(TicketType) == 0:
    print("请求票种信息失败，尝试是手动获取或者重试")
    exit(0)
idlist = []
print("----------------------------")
print("票种信息如下：")
for i in TicketType:
    print(f"ID:{i['id']}---Name:{i['ticketName']}")
    idlist.append(str(i['id']))
print("-----------------------")
## 网络不好的话 请固定tid VIPDay1 1904
tid = ''
while True:
    tmp = input("请输入需要抢票的票种ID: ")
    if tmp in idlist:
        tid= tmp
        break
    else:
        print("ID输入错误")
## 自己选择购票人信息
ids = get_purchaser(token)
if len(ids)==0:
    print("请在账号中添加购票人信息。")
    exit(0)
purchaser_ids=''
count=0
while True:
    tmp = input("请输入购票人ID(多选时中间使用,隔开eg:123,222): ")
    selected_ids = tmp.split(',')
    if all(x in ids for x in selected_ids):
        purchaser_ids = tmp
        count = len(selected_ids)
        break
    else:
        print("购票人选择有误请重新选择")
# count = len(ids) ## 抢票的数量 几个人几张 
# for i in ids:
#     purchaser_ids += str(i)+","
# if purchaser_ids.endswith(","):
#     purchaser_ids = purchaser_ids[:-1]
## todo 手动选择购票人
print("start ...")
## 若只进行最后一步 记住上面打印的值填在这儿 之后注释上面的从填账号开始的地方
# token=""
# tid="" #票种ID
# count=""  # 购票数量
# purchaser_ids=""  # "12345,23456"

req_time = 3
while True:
    t = input("请输入请求等待时间（单位s）默认3s :")
    if t.isdigit():
        req_time = int(t)
        break
    else:
        print("输入一个数字")
## 建议开抢之前再使用
## 单线程 可自己优化为多进程
commit(token,tid,count,purchaser_ids,req_time)