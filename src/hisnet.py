import requests
import copy
from datetime import datetime

# custom modules
from String import String


# payload used for Hisnet login
login_payload = {
    'part': '',
    'f_name': '',
    'agree': '',
    'Language': 'Korean',               # English is another option
    'id': '',                           # need to set
    'password': '',                     # need to set
    'x': '15',
    'y': '15'
}

# common header for browsing hisnet links
headers = {
    'Referer' : String.URL.HOME.value,
    'User-Agent' : String.NAME.value,
    'Host': String.REQ_HOST.value,
    'Origin': String.URL.HOME.value,
    'Cookie' : 'PHPSESSID='
}


def is_valid_id_pw(text:str):
    if len(text) < 4:
        return False
    if ('"' in text) or ("'" in text):
        return False
    return True


# gets new PHPSESSID value from Hisnet homepage, which is used as session cookie
def get_random_session() -> str:
    r = requests.get(String.URL.HOME.value)             # without sending any header, homepage will provide appropriate session value
    header = r.headers.pop('Set-Cookie')
    sid = header.split()[0].split('=')[1][:-1]          # extracts PHPSESSID value only
    return sid


# gets authentication for a user's session
def login_user(user_data:dict) -> bool:
    if not is_valid_id_pw(user_data['id']):
        return False
    if not is_valid_id_pw(user_data['pw']):
        return False

    login_payload_copy = copy.deepcopy(login_payload)
    login_payload_copy['id'] = user_data['id']
    login_payload_copy['password'] = user_data['pw']

    headers_copy = copy.deepcopy(headers)
    headers_copy['Cookie'] = 'PHPSESSID=' + user_data['session']
    
    r = requests.post(String.URL.LOGIN.value, data=login_payload_copy, headers=headers_copy)
    
    if('존재하지 않는 아이디 입니다' in r.text):
        print('no such id exist')
        return False
    elif('비밀번호가 기존 비밀번호와 일치하지 않습니다' in r.text):
        print('wrong password')
        return False
    else:
        print('login success')
        return True


def get_user_student_no(user_data:dict) -> str:
    # assumes that user has authorized session
    headers_copy = copy.deepcopy(headers)
    headers_copy['Cookie'] = 'PHPSESSID=' + user_data['session']
    r = requests.get(String.URL.MAIN.value, headers=headers_copy)
    idx = r.text.find(String.STUD_NO_FIND.value) + len(String.STUD_NO_FIND.value)
    student_id = r.text[idx:idx+8]
    return student_id
    

# tries to access to MAIN page and checks if logged in or not
def is_session_valid(user_data:dict) -> bool:
    headers_copy = copy.deepcopy(headers)
    headers_copy['Cookie'] = 'PHPSESSID=' + user_data['session']
    r = requests.get(String.URL.MAIN.value, headers=headers_copy)
    if 'Welcome' in r.text:
        return True
    elif '세션정보가 존재하지 않아 로그아웃 됩니다' in r.text:
        return False
    else:
        print('unknown response')
        return False

    