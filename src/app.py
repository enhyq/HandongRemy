from collections import UserDict
from crypt import methods
from logging import warning
from flask import Flask, request, jsonify
import random, sys, datetime, json

# custom modules
import room
import util
import menu
from users import Users
import hisnet
import rc

app = Flask(__name__)
users = Users()

warning_list = []
black_list = []

@app.route('/')
def hello():
    return 'Hello, World!'                          # test for live flask

# test api
@app.route('/api', methods=['POST'])
def parse():
    content = request.get_json()                    # request header data from Kako bot
    user = content['userRequest']['user']['id']     # distinct user id value for each Kako talk user
    print(f'user :: {user} :: has accessed')        # printout for testing
    return content
    content = content['userRequest']['utterance']   # utterance = '발화'


# functions that does not require login
@app.route('/api/random_number', methods=['POST','GET'])   # returns random number between 1 to 10 (inclusive)
def random_number():
    return util.make_simple_text_json_response("랜덤숫자: " + str(random.randint(1, 10)))

@app.route('/api/today_menu', methods=['POST','GET'])
def today_menu():
    utterance = request.get_json()['userRequest']['utterance']
    # later could add function that orders corner list by the popularity(number) of people selecting each item
    corner_list = ['든든한동', '따스한동', 'H-Plate', '맘스', '그레이스 가든']
    if utterance == '오늘 메뉴 알려줘':
        return util.make_simple_text_json_response_with_quick_replies(
            '어느 코너의 메뉴를 찾으시나요?',
            corner_list
            )
    else:
        return util.make_simple_text_json_response_with_quick_replies(
            menu.get_today_menu(utterance),
            corner_list
            )


@app.route('/api/simple_room', methods=['POST', 'GET'])      # checks if any room is available at the moment
def room_summary():
    content = request.get_json()
    # print(content)
    additional_action = ['다른 날짜/시간대 확인']
    utterance = content['userRequest']['utterance']
    if utterance == additional_action[0]:
        selected_date = content['action']['detailParams']['date']['origin']
        selected_time = content['action']['detailParams']['time']['origin']
        
        room_result = room.get_current_empty_room(selected_date, selected_time)
        available_rooms = room_result.split('\n')[1:] # first part is text
        q_m_label_list = available_rooms
        a_m_message_list = [(selected_date + ' ' + i) for i in available_rooms]

        return util.make_simple_text_json_response_with_quick_replies(
            room_result,
            additional_action + q_m_label_list,
            additional_action + a_m_message_list
            )
    elif utterance == '비어있는 상상랩':
        room_result = room.time_taken()
        available_rooms = room_result.split('\n')[1:] # first part is text
        q_m_label_list = available_rooms
        return util.make_simple_text_json_response_with_quick_replies(
            room_result,
            additional_action + q_m_label_list
            )
    elif '상상랩' in utterance:  # request for detailed room information
        selected_room = content['userRequest']['utterance'][-1] # if 0, then 10
        text = ''
        if content['action']['detailParams']:
            selected_date = content['action']['detailParams']['sys_date']['origin']
            text = room.get_detailed_room_info(selected_room, selected_date)
        else:
            text = room.get_detailed_room_info(selected_room)
        return util.make_simple_text_json_response(text)
    else:
        print('How did this got executed?')
        print(content)
        return util.make_simple_text_json_response('this is bug!')

# login
@app.route('/api/login', methods=['POST'])
def login():
    content = request.get_json()
    kakao_id = content['userRequest']['user']['id']
    # check if already login
    # after the first successful login, the login parameter values does not matter
    if users.is_user_registered(kakao_id):
        data = users.get_user_data(kakao_id)
        user_id = data['id']
        return util.make_simple_text_json_response(f"이미 {user_id}님으로 로그인 되어 있습니다!")
    # check if black list
    if kakao_id in warning_list:
        if kakao_id in black_list:
            return util.make_simple_text_json_response("너무 많이 틀려서 안돼요. 로그인 하고 싶으면 관리자에게 문의하세요")

    # check if valid id and pw
    hisnet_id = content['action']['params']['hisnet_id']
    hisnet_pw = content['action']['params']['hisnet_pw']

    if not hisnet.is_valid_id_pw(hisnet_id):
        if kakao_id in warning_list:
            if kakao_id not in black_list:
                black_list.append(kakao_id)
        else:
            warning_list.append(kakao_id)
        return util.make_simple_text_json_response('허용되지 않는 입력 값 입니다')
    if not hisnet.is_valid_id_pw(hisnet_pw):
        if kakao_id in warning_list:
            if kakao_id not in black_list:
                black_list.append(kakao_id)
        else:
            warning_list.append(kakao_id)
        return util.make_simple_text_json_response('허용되지 않는 입력 값 입니다')

    # {'id' : value, 'pw' : value, 'student_id' : value, 'session' : value}
    # print(content)
    temp_user_data = {}
    temp_user_data['id'] = hisnet_id
    temp_user_data['pw'] = hisnet_pw
    temp_user_data['session'] = hisnet.get_random_session()
    if not hisnet.login_user(temp_user_data):
        if kakao_id in warning_list:
            if kakao_id not in black_list:
                black_list.append(kakao_id)
        else:
            warning_list.append(kakao_id)
        return util.make_simple_text_json_response('로그인에 실패했습니다')
    print('login success ???')

    if hisnet.is_session_valid(temp_user_data):
        temp_user_data['student_id'] = hisnet.get_user_student_no(temp_user_data)
    else:
        # at this point assume user id and pw are correct
        hisnet.login_user(temp_user_data)
        temp_user_data['student_id'] = hisnet.get_user_student_no(temp_user_data)
    
    users.user_data[kakao_id] = temp_user_data   # main user에 추가
    stud_id = temp_user_data['student_id']
    return util.make_simple_text_json_response(f'{stud_id}님으로 로그인 되었습니다')


# function that require login
@app.route('/api/apply_room', methods=['POST'])
def apply_room():
    # first check if user is valid
    content = request.get_json()
    kakao_id = content['userRequest']['user']['id']

    if not users.is_user_registered(kakao_id):
        return util.make_simple_text_json_response('로그인이 필요한 기능입니다!')

    # even though user is logged in, the session could have been expired
    # check session validity
    if not hisnet.is_session_valid(users.get_user_data(kakao_id)):
        # renew session if session not valid
        hisnet.login_user(users.get_user_data(kakao_id))

    # get all the data from request data
    content = request.get_json()
    room_no = content['action']['detailParams']['room_no']['value']
    date = content['action']['detailParams']['date']['value'].split(':')[-1].split('"')[1]
    # print(content['action']['detailParams']['start_time']['value'].split('"')[-2].split(':'))
    
    start_time_hour, start_time_min, sts = list(map(int, content['action']['detailParams']['start_time']['value'].split('"')[-2].split(':')))
    end_time_hour, end_time_min, sts = list(map(int, content['action']['detailParams']['end_time']['value'].split('"')[-2].split(':')))

    if (start_time_hour > end_time_hour) or (start_time_hour==end_time_hour and start_time_min>=end_time_min):
        return util.make_simple_text_json_response('시작 시간이 끝나는 시간보다 늦을 수 없습니다')
    
    # conference room 1 assigend to room number 88
    # therefore add the room number to 87 to get the apply room number
    apply_room_number = str(87 + int(room_no))
    
    room_data = {
        'gbn': apply_room_number,              # room number
        'selDate': date,          # date in format ex) 2022-06-11
        'starttime': f'{start_time_hour:02d}{start_time_min:02d}',        # ex) 0900 time
        'endtime': f'{end_time_hour:02d}{end_time_min:02d}'               # ex) 1000 time
    }

    # print(start_time_hour, end_time_hour, date)
    # max reserve time should not exceed 3 hours
    # hisnet server checks for it so don't need to worry about that
    # print(users.user_data)
    apply_result = room.apply_room(users.get_user_data(kakao_id), room_data)

    if apply_result == False:
        return util.make_simple_text_json_response('예약에 실패 했습니다. 해당 시간에 자리가 예약이 이미 되어있는지 다시 한번 확인해주세요')
    elif apply_result == True:
        return util.make_simple_text_json_response(f'{date} {start_time_hour:02d}:{start_time_min:02d} ~ {end_time_hour:02d}:{end_time_min:02d}에 상상랩{room_no}번을 예약했습니다')


# currently only today's sleep over apply is possible
@app.route('/api/apply_sleepover', methods=['POST'])
def apply_sleepover():
    # first check if user is valid
    content = request.get_json()
    kakao_id = content['userRequest']['user']['id']
    if not users.is_user_registered(kakao_id):
        return util.make_simple_text_json_response('로그인이 필요한 기능입니다!')

    # even though user is logged in, the session could have been expired
    # check session validity
    if not hisnet.is_session_valid(users.get_user_data(kakao_id)):
        # renew session if session not valid
        hisnet.login_user(users.get_user_data(kakao_id))

    # apply sleep over for today
    result = rc.apply_sleepover(users.get_user_data(kakao_id))
    if result == False:
        return util.make_simple_text_json_response('외박 신청에 실패했습니다')
    
    return util.make_simple_text_json_response('외박이 신청되었습니다')

if __name__ == '__main__':
    app.run()
    