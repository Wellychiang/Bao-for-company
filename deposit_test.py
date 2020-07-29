import allure
import time
import baoApi.bao
import pytest
import logging
import re
from colorama import init


logging.basicConfig(level=logging.DEBUG, filename='deposit.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
init(autoreset=True)

b = baoApi.bao


@allure.feature('Positive')
@allure.step('step')
@pytest.mark.run(order=6)
def test_deposit_success_without_cards(username='jackson', pwd='a111222', amount=20, service_type=None):
    a_type = [
         'WebATM', 'WeiXinScan', 'AlipayScan', 'SpeedyPay', 'UnionPayScan', 'UnionPayFlash'
            ]
    if service_type is None:
        service_type = a_type
    b.login(username, pwd)
    '''
    WebATM(網銀在線),  WeiXinScan(支付寶轉卡),
    AlipayScan(支付寶掃碼), SpeedyPay(快捷支付), UnionPayScan(銀連支付掃碼), UnionPayFlash(雲閃付)
    '''
    for all_type in service_type:
        deposit = b.deposit(amount, all_type)
        print(deposit)
        if deposit['msg'] == '成功':
            lis = [
                 deposit['status_code'] == 200,
                 deposit['status'] == 'OK',
                 deposit['msg'] == '成功',
                 deposit['serviceType'] == all_type,
                 int(deposit['amount']) == amount,
                 int(deposit['finalAmount']) == amount,
                 'http://register.sit.apollo.ark88.local/Gateway/Pay' in deposit['url'],
                 deposit['countDownTimeSec'] < 1000,
                 deposit['returnMessage'] == '成功',
                ]
        else:
            raise ValueError('Deposit failed')
        error = 0
        count = 0
        for judge in lis:
            count += 1
            if not judge:
                error += 1
                logging.debug('Service type: %s' % all_type)
                logging.debug('lis的第%s行' % count)

        if error >= 1:
            logging.debug('Correct Message: %s, lis: %s' % (deposit, lis))
            raise AssertionError(
                "\tError count : %s\n%s" % (error, time.strftime('%Y-%m-%d %H:%M:%S')))


@allure.feature('Positive')
@allure.step('step')
@pytest.mark.run(order=7)
# 可以用XPATH補一下應收帳款response的號碼
def test_deposit_card_success(username='jackson', pwd='a111222', amount=50, service_type=None):
    # DirectPay(卡對卡), WeiXin(微信轉卡), Alipay(支付寶轉卡)

    count = 0
    error = 0

    b.login(username, pwd)
    if service_type is None:
        service_type = ['DirectPay', 'WeiXin', 'Alipay']

    for typ in service_type:
        cards = b.deposit(amount, typ)
        # text = re.findall("")
        print()
        if '123456789' in cards['text']:
            lis = [
                cards['status_code'] == 200,
                '50' in cards['text'],
                '123456789' in cards['text']
                   ]

            for judge in lis:
                count += 1
                if not judge:
                    error += 1
                    logging.debug('\tlis的第%s行錯誤' % count)

            if error >= 1:
                raise AssertionError(
                    "\tError count : %s\n%s" % (error, time.strftime('%Y-%m-%d %H:%M:%S')))
        else:
            raise ValueError("%sReceivable's account incorrect with 123456789, text: %s"
                             % username, cards['text'])

