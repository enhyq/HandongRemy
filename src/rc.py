from datetime import datetime
import requests

# custom module
from String import String

def apply_sleepover(user_data:dict) -> bool:
    # assume that hisnet session is valid

    # login directly from rc main page takes more than 5 seconds to load
    # which not good for using it in Kakao talk bot api

    now = datetime.now()
    apply_date = now.strftime('%Y-%m-%d')
    now_str = now.strftime('%Y%m%d%H%M%S')
    
    # can't apply after 23:00
    if now.hour == 23:
        return False

    # get random jsession id
    r = requests.get('https://rc.handong.edu/rc/index.do')
    jsession = r.headers['Set-Cookie']  # ex) 'JSESSIONID=F20CBD6DDFF2E97D402BB1F4555C96EE; Path=/; Secure; HttpOnly'
    jsession = jsession.split(';')[0]

    request_1_header = {
        'Cookie' : 'PHPSESSID=' + user_data['session'],
        'Host': String.REQ_HOST.value,
        'Origin': String.URL.HOME.value,
        'Referer': String.URL.MAIN.value
    }
    request_1_data = {
        'userid': user_data['id'],
        'token': now_str
    }
    r_1 = requests.post('https://hisnet.handong.edu/dormitory_sso.php', headers=request_1_header, data=request_1_data)

    if not 'https://rc.handong.edu/rc/login_sso.do' in r_1.text:
        return False
    
    request_2_header = {
        'Cookie' : jsession,
        'Host': String.RC_HOST.value,
        'Origin': String.URL.HOME.value,
        'Referer': String.URL.HOME.value
    }
    request_2_data = {
        'user_num': user_data['student_id'],
        'hash_key': now_str
    }
    
    r_2 = requests.post('https://rc.handong.edu/rc/login_sso.do', headers=request_2_header, data = request_2_data)

    # no response?
    print(r_2.status_code)
    print(jsession)
    # login success

    # request sleep over
    sleepover_header = {
        'Cookie' : jsession,
        'Host': String.RC_HOST.value,
        'Origin': String.URL.RC_HOME.value,
        'Referer': String.URL.RC_SLEEPOVER_REFERER.value
    }
    sleepover_data = {
        'flag': '1',
        'menu_idx': '70',
        'syrst': '20221',
        'editMode': 'ADD',
        'ovng_begin_dttm': apply_date,
        'ovng_diff': '1',
        'ovng_resn': ''
    }
    
    r_a = requests.post(String.URL.RC_SLEEPOVER_APPLY.value, headers=sleepover_header, data=sleepover_data)
    print(r_a.text)

    if '외박 신청이 완료되었습니다.' in r_a.text:
        return True
    
    print('외박 신청이 실패했습니다')
    return False