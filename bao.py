import logging
import requests
import json
from colorama import init
import re
import pytest


logging.basicConfig(level=logging.DEBUG, filename='basic_tools.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


init(autoreset=True)

s = requests.session()


# @pytest.fixture(scope='funtion', autouse=True)
def login(username, pwd):
    url = "http://sit.frontside.web.gt.owms.ark88.local:7878/E7/MerchantFrontSide/Account/Login"
    rr = s.get(url)

    global cookie

    try:
        cookies = re.findall("Cookie (.*) for", str(rr.cookies))
        cookie = cookies[0]
    except Exception as e:
        print(e)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookie
    }

    token = re.findall('<input name="__RequestVerificationToken" type="hidden" value="(.*)" />', rr.text)

    data = {
        "__RequestVerificationToken": token,
        "UserName": username,
        "UserPwd": pwd
    }
    #  requests.session記得放在全局

    try:
        logging.debug('start to post by login')
        r = s.post(url, headers=headers, data=data, allow_redirects=False)
        updateCookie = r.headers["Set-Cookie"]
        logging.debug("\npost: %s" % r.status_code)

    except Exception:
        logging.debug('status_code: %s\n text: %s' % (r.status_code, r.text))
        return r.text

    else:
        url2 = "http://sit.frontside.web.gt.owms.ark88.local:7878/E7"
        headers2 = {"Cookie": "%s" % updateCookie}
        logging.debug('start to get')
        r2 = s.get(url2, headers=headers2)
        logging.debug("get: %s" % r2.status_code)
        lis = {
            'text': r2.text,
            'status_code': r2.status_code
        }
        return lis


def member_add(user, init_num,  arrive_num):

    url = "http://sit.frontside.web.gt.owms.ark88.local:7878/E7/MerchantFrontSide/Member/MemberAdd"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    for i in range(arrive_num):
        init_num += 1
        data = {
            "Account": "%s%s" % (user, init_num),
            "Password": "a111222",
            "RebatePro": "4.000"
            }
        r = s.post(url, headers=headers, data=data)
        logging.debug(r.json(), "\n%s%s" % (user, init_num))


def deposit(amount, service_type):
    url = "http://sit.frontside.web.gt.owms.ark88.local:7878/E7/MerchantFrontSide/Financial/ChargeInfo"

    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = {
        "Amount": "%s" % amount,
        "ServiceType": "%s" % service_type
            }
    logging.debug('Start to post by deposit')
    r = s.post(url, headers=headers, data=data)
    logging.debug('Post: %s' % r.text)
    try:
        if r.json()['msg'] == '成功':
            logging.debug("Success session")
            li = {
                'status_code': r.status_code,
                'status': r.json()['status'],
                'msg': r.json()['msg'],
                'serviceType': r.json()['result']['dataModel']['serviceType'],
                'amount': r.json()['result']['dataModel']['amount'],
                'finalAmount': r.json()['result']['dataModel']['finalAmount'],
                'url': r.json()['result']['dataModel']['url'],
                'countDownTimeSec': r.json()['result']['dataModel']['countDownTimeSec'],
                'returnMessage': r.json()['result']['returnMessage']
                  }

        elif r.json()['msg'] == 'IP或地域限制，您无充值线路可使用，详情请联系客服':
            raise ValueError(r.json()['msg'])

        else:
            logging.debug("Failed session")
            li = {
                'msg': r.json()['msg'],
                'returnMessage': r.json()['returnMessage']
            }

        return li
    except Exception:
        logging.debug('The exception')
        li = {
            'text': r.text,
            'status_code': r.status_code
        }
        return li


def withdraw(username, funds_pwd, amount):
    """Need to create your card id first"""
    Score = get_user_score()
    url = "http://sit.frontside.web.gt.owms.ark88.local:7878/E7/MerchantFrontSide/Financial/Withdraw"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    if username == 'wade01':
        card_id = 'C7549D972BC06A89B7357C623501613B2B030F2B3464FE' \
                  'C30AE01E80C003D01EFBA0BD799FDE5FF3F3B6EE21FC9B085462ECEB7D6630ACE2CD058E1F872A2562'
    elif username == 'wade02':
        card_id = '76C7D70A406B0BB798CFC7EE4E5342F724B2CC15216F6F' \
                  'C85D48805876D9B3A6F15BEA0FD8F6AF2FA9AFB10D221B8D19233D0FAABA04C475B764511F4335CCF5'
    elif username == 'test03':  # 沒卡
        card_id = '1A6445E43285E71B3B61A84F5E176911AD9B7D8CFCE1838' \
                  '0C09DDCDF41060BBEE1ED0A42BD55AE5889B02FBC77D7E9E3E9F269ED25F0B57A4290A9766394739E'
    elif username == 'test05':  # 沒錢
        card_id = 'A0C65773A5317AA4DEFD4043B8345CA58165C2916E51F949' \
                  '41C6958D8350EF9DBACFDC74314C5B47C3BFD0CB1805B89076C9E72091B5A54BD26BBB48422196E3'
    elif username == 'test08':
        card_id = 'E716369D1CD21D972302A5953A473883A265A9F461468C89C' \
                  '3AD7ED99D4D05A1BB68E765C85F8CB3E447CAE10B9ACE30D14AB61FCA8659795FD54747F1591E42'
    elif username == 'jackson':
        card_id = 'D5EDA8FB45AEB03AD2D53627F109E0E1B09F0CF19DB9158F7' \
                  '82D75BB2B716278A322D13ADC136B8EA9922914B38C140ABC3CBC96A349371FB2BA4DA739E5E69D'
    else:
        card_id = 'C7549D972BC06A89B7357C623501613B2B030F2B3464FEC30' \
                  'AE01E80C003D01EFBA0BD799FDE5FF3F3B6EE21FC9B085462ECEB7D6630ACE2CD058E1F872A2562'

    data = {
        "CardId": card_id,
        "AvailableScore": Score['aScore'],
        "UserName": "%s" % username,
        "Amount": "%s" % amount,
        "MoneyPassword": funds_pwd
    }

    logging.debug('Start to post by withdraw')
    r = s.post(url, headers=headers, data=data)
    logging.debug('Post: %s' % r.text)
    try:
        if r.json()['msg'] == '資訊不完整':
            logging.debug('Incomplete session')
            lis = {
                'status_code': r.status_code,
                'status': r.json()['status'],
                'msg': r.json()['msg']}
            return lis

        elif r.json()['msg'] == '成功':
            logging.debug('Success session')
            lis = {
                    'status_code': r.status_code,
                    'status': r.json()['status'],
                    'msg': r.json()['msg'],
                    'amount': r.json()['result']['dataModel']['amount'],
                    'availableScore': r.json()['result']['dataModel']['availableScore'],
                    'returnMessage': r.json()['result']['returnMessage']
                }
            return lis

        else:
            logging.debug('The other session')
            lis = {
                    'status_code': r.status_code,
                    'status': r.json()['status'],
                    'msg': r.json()['msg'],
                    'returnMessage': r.json()['result']['returnMessage']
                }
            return lis

    except Exception:
        logging.debug('錯了啦')


def bet_qq(amount, chi_hao):

    url = "http://sit.frontside.web.gt.owms.ark88.local:7878/E7/MerchantFrontSide/Lottery/Plays"
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    data = {
        "betAmount": "%s" % amount,
        "betCount": "1",
        "currencyUnit": "1",
        "drawNumber": "5",
        "issueNo": "%s" % chi_hao,
        "lotteryId": "27",
        "odds": "3.653",
        "playTypeId": "20",
        "playTypeRadioId": "116",
        "ratio": "1",
        "rebate": "0",
        "totalBetAmount": "%s.0000" % amount,
        "userType": "2"
        }

    load = json.dumps(data)
    logging.debug('Start to post by bet_qq')
    r = s.post(url, headers=headers, data=load)
    logging.debug('Post: %s' % r.json())
    return r.json()


def get_user_score():

    url = "http://sit.frontside.web.gt.owms.ark88.local:7878/E7/MerchantFrontSide/Home/GetUserScore"
    logging.debug('Start to get by get user score')
    r = s.get(url)
    logging.debug('Get: %s' % r.text)
    a = {'aScore': r.json()['result']['aScore']}
    return a

