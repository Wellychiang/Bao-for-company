import bao
import time
import allure
import pytest
import logging


b = bao
logging.basicConfig(level=logging.DEBUG, filename='withdraw.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# @allure.feature('Positive')
# @allure.step('step')
# @pytest.mark.run(order=2)
# 可用wade01, jackson
def test_withdraw_success(user='wade01', pwd='a111222', fund_pwd='a12345', amount=20):
    # global lis
    count = 0
    error = 0

    b.login(user, pwd)
    withdraw = b.withdraw(user, fund_pwd, amount)
    time.sleep(1)
    score = b.get_user_score()

    if withdraw['msg'] == '成功':
        lis = [
            withdraw['status_code'] == 200,
            withdraw['status'] == 'OK',
            withdraw['msg'] == '成功',
            withdraw['amount'] == amount,
            f"{withdraw['availableScore']:,.4f}" == score['aScore'],
            withdraw['returnMessage'] == '成功'
        ]

    else:
        raise ValueError('The other message without 成功')

    for judge in lis:
        count += 1
        if not judge:
            error += 1
            logging.debug('錯在lis的第%s行' % count)

    if error >= 1:
        raise AssertionError("\tError count : %s\nCurrent response: %s\n%s" %
                             (error, withdraw, time.strftime('%Y-%m-%d %H:%M:%S')))


# @allure.feature('Minus')
# @allure.step('step')
# @pytest.mark.run(order=3)
# 目前判斷有無帳號卡、金額邊界(20~499)的response資料是否正確,有可以判斷錯誤在哪的簡易機制(判定當下組別所有錯誤)
# name變數裡的值"第一個"必須要是有足夠餘額有卡的, 第二個要是沒卡的
def test_withdraw_with_incomplete_fundpassword_and_nobinding(name=None, range_num=2, pwd='a111222'):
    if name is None:
        name = ['wade01', 'wade03']
    fun_pwd = ['a12345', '', '       ', '我的天ㄚㄚㄚ', '!@#!@#!@#', 'a1234', 'a123456789012345']
    a_amount = ['', 0, 19, 20, 499, 500]

    global lis
    error = 0
    count = 0
    wade01_success = 0
    wade01_quota = 0  # 限額
    wade03_no_card = 0
    wade01_info_incomplete = 0
    wade03_info_incomplete = 0
    wade01_wrong_fund_pwd = 0

    for i in range(range_num):
        for username in name:
            b.login(username, pwd)
            for amount in a_amount:
                for fund_pwd in fun_pwd:
                    withdraw = b.withdraw(username, fund_pwd, amount)
                    time.sleep(1)
                    score = b.get_user_score()

                    if username == name[0]:
                        if withdraw['msg'] == '成功':
                            wade01_success += 1
                            logging.debug('%s成功流程' % username)

                            lis = [
                                withdraw['status_code'] == 200,
                                withdraw['status'] == 'OK',
                                withdraw['msg'] == '成功',
                                withdraw['amount'] == amount,
                                f"{withdraw['availableScore']:,.4f}" == score['aScore'],
                                withdraw['returnMessage'] == '成功'
                            ]

                        elif withdraw['msg'] == '单日提现及下线转账次数不可超过20次':
                            raise ValueError("\t%s out of twenty times" % username)

                        elif withdraw['msg'] == '余额不足':
                            raise ValueError("\t%s hasn't enough money" % username)

                        elif withdraw['msg'] == '单次提现限额为20~499，请重新输入':
                            logging.debug('%s限額20~499流程' % username)
                            wade01_quota += 1

                            lis = [
                                withdraw['status_code'] == 200,
                                withdraw['status'] == 'NG',
                                withdraw['msg'] == '单次提现限额为20~499，请重新输入',
                                withdraw['returnMessage'] == '单次提现限额为20~499，请重新输入'
                            ]

                        elif withdraw['msg'] == '資訊不完整':  # 未輸入、空白導致的資訊不完整(不管是資金密碼或是錢)
                            wade01_info_incomplete += 1
                            logging.debug('%s資訊不完整流程' % username)

                            lis = [
                                withdraw['status_code'] == 200,
                                withdraw['status'] == 'NG',
                                withdraw['msg'] == '資訊不完整'
                                ]

                        elif withdraw['msg'] == '资金密码不正确，请重新输入':  # 除了空白和未輸入以外導致的資金密碼不正確
                            wade01_wrong_fund_pwd += 1
                            logging.debug('%s资金密码不正确流程' % username)

                            lis = [
                                withdraw['status_code'] == 200,
                                withdraw['status'] == 'NG',
                                withdraw['msg'] == '资金密码不正确，请重新输入',
                                withdraw['returnMessage'] == '资金密码不正确，请重新输入'
                            ]

                        else:
                            raise ValueError(
                                "%s's unknown scenario for withdraw's msg\n the current response : %s "
                                % (username, withdraw)
                                )

                    elif username == name[1]:
                        if withdraw['msg'] == '您尚未绑定银行卡，请先进行绑定方能提现。':  # 尚未綁定銀行卡的狀況下輸入除了空白以外都會
                            wade03_no_card += 1
                            logging.debug('%s尚未綁定銀行卡流程' % username)

                            lis = [
                                withdraw['status_code'] == 200,
                                withdraw['status'] == 'NG',
                                withdraw['msg'] == '您尚未绑定银行卡，请先进行绑定方能提现。',
                                withdraw['returnMessage'] == '您尚未绑定银行卡，请先进行绑定方能提现。'
                            ]

                        elif withdraw['msg'] == '資訊不完整':  # 未輸入、空白導致的資訊不完整(不管是資金密碼或是錢)
                            wade03_info_incomplete += 1
                            logging.debug('%s資訊不完整流程' % username)

                            lis = [
                                withdraw['status_code'] == 200,
                                withdraw['status'] == 'NG',
                                withdraw['msg'] == '資訊不完整'
                                ]

                    else:
                        raise ValueError("Unknown value error with username\nCurrent username: %s" % username)

                    for judge in lis:
                        count += 1
                        if not judge:
                            error += 1
                            logging.debug('錯在lis的第%s行' % count)

                    if error >= 1:
                        raise AssertionError("\tError count : %s\nCurrent response: %s\n%s" %
                                             (error, withdraw, time.strftime('%Y-%m-%d %H:%M:%S')))

    assert wade03_no_card == 25*range_num \
        and wade03_info_incomplete == 17*range_num\
        and wade01_quota == 3*range_num \
        and wade01_info_incomplete == 17*range_num \
        and wade01_wrong_fund_pwd == 20*range_num \
        and wade01_success == 2*range_num \



# @allure.feature('Minus')
# @allure.step('step')
# @pytest.mark.run(order=4)
# 可用test05
def test_withdraw_with_not_enough_money(username='test05', pwd='a111222', funds_pwd='a12345', amount=20):

    not_enough_money = 0
    count = 0
    error = 0

    b.login(username, pwd)
    withdraw = b.withdraw(username, funds_pwd, amount)
    if withdraw['msg'] == '余额不足':
        not_enough_money += 1

        lis = [
            withdraw['status_code'] == 200,
            withdraw['status'] == 'NG',
            withdraw['msg'] == '余额不足',
            withdraw['returnMessage'] == '余额不足'
        ]

        for judge in lis:
            count += 1
            if not judge:
                error += 1
                logging.debug('錯在lis的第%s行' % count)

        if error >= 1:
            raise ValueError('Error count: %s\nCurrent response: %s\n%s' %
                             (error, withdraw, time.strftime('%Y-%m-%d %H:%M:%S')))

    else:
        raise ValueError("This scenario's response incorrect: %s\n%s" %
                         (withdraw, time.strftime('%Y-%m-%d %H:%M:%S')))


# @allure.feature("Minus")
# @allure.step('step')
# @pytest.mark.run(order=5)
# 須今日無任何提現紀錄的帳號測試
# around_times輸入的次數就等於超過20之後的次數
# 確認msg出現"系統錯誤"的情境後排除(已排除)
# 可用test08, wade02
def test_withdraw_with_twenty_times(username='wade02', pwd='a111222', funds_pwd='a12345', amount=20, around_times=1):

    global lis
    over_twenty_times = 0
    error = 0
    count = 0
    times = 0
    success_time = 0

    b.login(username, pwd)

    for i in range(int('20')+int('%s' % around_times)):
        withdraw = b.withdraw(username, funds_pwd, amount)
        time.sleep(0.8)
        times += 1

        if withdraw['msg'] == '单日提现及下线转账次数不可超过20次':
            logging.debug('第%s次超過20次的提現流程' % over_twenty_times)
            over_twenty_times += 1

            lis = [
                withdraw['status_code'] == 200,
                withdraw['status'] == 'NG',
                withdraw['msg'] == '单日提现及下线转账次数不可超过20次',
                withdraw['returnMessage'] == '单日提现及下线转账次数不可超过20次'
            ]

        elif withdraw['msg'] == '成功':
            success_time += 1
            logging.debug('Sucess times:', success_time)
            pass

            for judge in lis:
                count += 1
                if not judge:
                    error += 1
                    logging.debug('錯在lis的第%s行' % count)
            logging.debug('Response msg: ', withdraw)

        else:
            raise ValueError("This scenario's response incorrect, current response: %s\n%s" %
                             (withdraw, time.strftime('%Y-%m-%d %H:%M:%S')))
        if error >= 1:
            raise ValueError('Error count: %s\nCurrent response%s\n%s' %
                             (error, withdraw, time.strftime('%Y-%m-%d %H:%M:%S')))

    if around_times != over_twenty_times:
        raise AssertionError("\tAround_times: %s\tOver_twenty_times: %s\n%s" % (
            around_times, over_twenty_times, time.strftime('%Y-%m-%d %H:%M:%S')))

# # 用戶等級不一樣提款限額也不一樣
# def test_single_withdraw_with_the_quota():

