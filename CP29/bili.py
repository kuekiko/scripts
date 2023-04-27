import requests
import time
import json

## 容易触发B站风控策略 勿用

# COOKIE = f"buvid3=E00263AA-278D-8F6A-E2E2-111111; b_nut=1673763754; i-wanna-go-back=-1; _uuid=52FE7F98-AB57-6D9D-1022A-C716710811097B54720infoc; buvid4=50292EAB-439D-B9E8-48CC-E62C97F29D8394361-022080101-zVYRD9eIaXHBfOIJuisBhA%3D%3D; DedeUserID=6477559; DedeUserID__ckMd5=baee8d9b93b1e942; b_ut=5; nostalgia_conf=-1; rpdid=0zbfAHJowX|13DXtBe11|4E|3w1PgWtD; buvid_fp_plain=undefined; CURRENT_BLACKGAP=0; i-wanna-go-feeds=-1; LIVE_BUVID=AUTO1816738881388006; hit-new-style-dyn=0; hit-dyn-v2=1; CURRENT_QUALITY=120; is-2022-channel=1; header_theme_version=CLOSE; CURRENT_PID=613fca50-cd7d-11ed-b235-472145a61338; FEED_LIVE_VERSION=V8; fingerprint=a3b673f6d39d1d084da5b94c908b4d30; buvid_fp=383fd678550a6508a4493e631dc081c8; CURRENT_FNVAL=4048; PVID=2; innersign=1; bp_video_offset_6477559=787442903438852100; SESSDATA=50e90e7d%1111%2Cd1b5f%2A42; bili_jct=0b34cda003509b78bd50e963cbe04daf; sid=8ud8ni06; deviceFingerprint=3ea3005a7bb9e7b294e5e3a89501d48b; bsource=search_baidu; kfcFrom=mall_search_mall; Hm_lvt_909b6959dc6f6524ac44f7d42fc290db=1682249149; msource=pc_web; b_lsid=E96FE856_187ADF0ED8C; canvasFp=1; webglFp=1; screenInfo=2560*1440*24; feSign=11"
# 直接忽略
COOKIE = ""

## 主要为拿各种ID 和判断是否有票
def get_ticket_info():
    # url = "https://show.bilibili.com/api/ticket/project/get?version=134&id=72320"
    # headers = {
    #     "Pragma": "no-cache",
    #     "Cache-Control": "no-cache",
    #     "Sec-Ch-Ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
    #     "Sec-Ch-Ua-Mobile": "?0",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
    #     "Sec-Ch-Ua-Platform": "\"Windows\"",
    #     "Accept": "*/*",
    #     "Sec-Fetch-Site": "same-origin",
    #     "Sec-Fetch-Mode": "cors",
    #     "Sec-Fetch-Dest": "empty",
    #     "Referer": "https://show.bilibili.com/platform/detail.html?id=72320&noTitleBar=1&from=mall_search_mall",
    #     "Accept-Encoding": "gzip, deflate",
    #     "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    #     "Cookie": COOKIE,
    # }
    # response = requests.get(url, headers=headers)
    # print(response.text)
    # resText = response.json()
    # if data := resText.get("data"):
    #     if sale_flag := data.get("sale_flag"):
    #         if sale_flag == "预售中":
    #             screen_list = data.get("screen_list")
    #             ##
    #             for i in screen_list:
    #                 print(f"screen_id:{i['id']}-----{i['name']}")
    #                 ticket_list = i['ticket_list']
    #                 for i in ticket_list:
    #                     sku_id = i['id']
    #                     print(f"----sku_id:{sku_id}------")
    #             # todo
    #             return {"project_id": 72320,
    #                     "screen_id": 126698,
    #                     "sku_id": 380920}
    # else:
        # return {} 手动直接填吧
    return {"project_id": 72320,
                "screen_id": 126698,
                "sku_id": 380920}

## 126698 2023-05-02 周二 380920
## 126699 2023-05-03 周三 380936  price=8000

def get_ticket_token(info, count):
    url = "https://show.bilibili.com/api/ticket/order/prepare"
    headers = {
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Sec-Ch-Ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://show.bilibili.com/platform/detail.html?id=71352&from=pc_ticketlist",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cookie": COOKIE
    }
    data = {
        "project_id": info['project_id'],
        "screen_id": info['screen_id'],
        "sku_id": info['sku_id'],
        'count': count,
        'token': '',
        'order_type': 1
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.text)
    resText = response.json()
    if data := resText.get("data"):
        return data.get('token')
    else:
        return ""

def get_buyer(token):
    url = "https://show.bilibili.com/api/ticket/buyer/list?is_default&projectId=72320" ##写死了
    headers = {
        "Host": "show.bilibili.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "put-your-cookie-here",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
        "Referer": f"https://show.bilibili.com/platform/confirmOrder.html?token={token}&project_id=72320",
        "Origin": "https://show.bilibili.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Cookie": COOKIE
    }
    response = requests.get(url, headers=headers)
    # print(response.text)
    resText = response.json()
    if data:=resText.get("data"):
        return data['list']
    else:
        return []


def create(token,buyer_info):
    url = "https://show.bilibili.com/api/ticket/order/createV2"
    headers = {
        "Host": "show.bilibili.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "put-your-cookie-here",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
        "Referer": f"https://show.bilibili.com/platform/confirmOrder.html?token={token}&project_id=72320",
        "Origin": "https://show.bilibili.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Cookie": COOKIE
    }
    ##？？？ 默认第一个得了
    buyer_info_str = json.dumps([buyer_info[0]])
    print(buyer_info_str)
    timestamp = str(int(time.time()*1000))
    data = {
        "project_id": "72320",
        "screen_id": "126698",
        "sku_id": "380920",
        "count": "1",
        "pay_money": "8000",
        "order_type": "1",
        "timestamp": timestamp,
        "buyer_info": buyer_info_str,
        "token": token,
        "deviceId": "3ea3115a7bb9e7b294e5e3a89501d48a"
    }

    while True:
    # 拼接完整URL
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code!=200:
                print("请求抢票失败")
                print(response.text)
            else:
                
                res = response.json()
                errno = res.get('errno')
                if errno == 10009 | errno == 100001:
                    print(res.get('msg'))
                    print(response.text)
                elif errno == 100050:
                    ##失效
                    print(res.get('msg'))
                    return False
                else:
                    print("啥情况")
                    print(res)
            time.sleep(5)
        except Exception as e:
            print(f"发生异常: {e}")
            time.sleep(5)

while True:
    info = get_ticket_info()
    print(info)
    token = get_ticket_token(info, 1)
    ## 有效期限制
    print(token)
    ## 身份证信息 GET /api/ticket/buyer/list?is_default&projectId=72320
    buyer_info = get_buyer(token)
    # print(buyer_info)
    ## 可能有多个人 
    # 阻塞
    create(token,buyer_info)
