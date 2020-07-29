import logging
from colorama import init
import allure
import baoApi.bao
import time
import pytest

b = baoApi.bao
logging.basicConfig(level=logging.DEBUG, filename='login.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@allure.feature('Positive')
@allure.step('step')
@pytest.mark.run(order=1)
def test_login_success(user='wade01', pwd='a111222'):
    response = b.login(user, pwd)
    if '个人中心' in response['text'] and response['status_code'] == 200:
        logging.debug('Login success!')
    else:
        raise ValueError("Login failed, current response: %s" % response)


# 驗證點為正常登入,帳密正確與否, 第六次錯誤後輸入正確密碼會進入鎖IP頁面
# 記得跑完一次就要DB:userbehavior洗掉count次數, 商業後台IP控制刪掉
@allure.feature('Minus')
@allure.step("step")
@pytest.mark.run(order=8)
def test_login_failed(user=None):
    if user is None:
        user = ['', '#$@#$$@', '11111111111111111', '000000', 'wade10']
    password = ['', '#$@#$$@', '0', '11111111111111111', '000000', 'aaaaaa', '111111', 'a111222']

    count = 0
    error = 0
    outOfFiveTimes = 0

    for name in user:
        for pwd in password:
            failed = b.login(name, pwd)
            count += 1
            time.sleep(1)

            if "忘記密碼用" in failed:
                logging.debug("Login failed scenario success: %s" % count)
                error += 1
            elif '个人中心' in failed:
                raise ValueError("Login response shouldn't have 'personalCenter' in failed test")
            else:  # 這個要錯誤五次之後"第六次"鎖住, '第七次'輸入正確帳號密碼才會跳出鎖ip
                logging.debug(failed)
                outOfFiveTimes += 1

    logging.debug(time.strftime('%Y-%m-%d- %H:%M:%S'))
    assert error == len(user) * len(password) - 1 and outOfFiveTimes == 1


if __name__ == '__main__':
    pytest.main(['-s', '-v', '-r', '--alluredir', 'report'])
