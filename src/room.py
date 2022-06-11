from flask import request_started
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import multiprocessing as mp
from time import sleep
import copy

# custom imports
import timer
from String import String


t = timer.Timer()           # for measuring times for debug

# Conference room 88 ~ 97 are room#1 ~ room#10 and 98 is Coding Talk Room
# Access to reserved/empty data of each conference room does not require login information
room_numbers = [i for i in range(88, 98)] # only consider 'sangsang lab'.. for now exclude Coding talk which is room number 98

# only 'gubun' parameter is required, others are optional
# if only 'gubun' parameter is provided, today's date will be in the first column
# can reserve in between 6:00 ~ 24:00 or can say (6:00 ~ 23:45 (inclusive))
# can't reserve or see for time that has already passed
# can search for room reservation status using id or name tag with specific value
# e.g.) id/name = f202206071745
# %Y%m%d%H%M    <- strftime format
# maximum reservation time is 3 hrs per day


# booking payload
room_apply_payload = {
    'gbn': '',              # room number
    'selDate': '',          # date in format ex) 2022-06-11
    'starttime': '',        # 0900 time
    'endtime': ''           # 0930 time
}
# common header for browsing hisnet links
room_apply_heading = {
    'Referer' : String.URL.HOME.value,
    'User-Agent' : String.NAME.value,
    'Host': String.REQ_HOST.value,
    'Origin': String.URL.HOME.value,
    'Cookie' : 'PHPSESSID=',
    'Content-Type': 'application/x-www-form-urlencoded'     # this is important?
}

# created for multiprocessing
def is_room_empty(room_no, check_time, result) -> bool:
    # result should have the size of room_numbers list
    # check_time has format -> 202206071745

    # this_date has format -> 2022-06-07
    this_date = check_time[0:4] + '-' + check_time[4:6] + '-' + check_time[6:8]

    # using session makes it work faster
    t.start('request')
    # setting stream to True makes it faster?
    response = requests.get(String.URL.ROOM_T.value + str(room_no) + String.URL.ROOM_T_date_p.value + this_date)
    t.stop()

    if response.status_code != 200:
        print('something got wrong while requesting to Hisnet room page')
        return False

    # bs4 takes too long
    t.start('parse')
    target_index = response.text.find('f'+check_time)
    target_text = response.text[target_index-110:target_index]
    t.stop()

    if 'bookingactYes' in target_text:
        result[1] = True
        return True
    else:
        result[1] = False
        return False
    
    # bs4 code
    soup = BeautifulSoup(response.text, 'html.parser')
    data = soup.find(id='f'+check_time)
        

# function parameter로 날짜를 넘겨주고
# url parameter의 ThisDate의 값으로 날짜를 넣어주면 이 함수로 다른 날짜들의 현재 시간에 비어있는 상상랩 확인 가능
# this function takes about 12 seconds using raspberri pi and mobile tethering which is not acceptible
# kakaotalk only waits 5 seconds for server to response

# check_date format -> 2022-06-17
# check_time format -> 09:45:00
def get_current_empty_room(check_date:str='', check_time:str=''):
    now = datetime.now()                # server's current time
    current_hour = now.hour
    current_min = now.minute
    current_date = now.strftime('%Y%m%d')

    next_hour = current_hour
    if current_min < 15:
        next_min = 15
    elif current_min < 30:
        next_min = 30
    elif current_min < 45:
        next_min = 45
    else:
        next_min = 0
        next_hour = current_hour+1
    
    # hour and min are next hour and next min
    # date is current
    if check_date and check_time:
        check_date_hour, check_date_min = check_time.split(':')[:2]
        check_date_hour = int(check_date_hour)
        check_date_min = int(check_date_min)
        if (check_date_hour < current_hour) or (check_date_hour == current_hour and check_date_min<current_min):
            if check_date.replace('-', '') == current_date:
                return str(check_date_hour) +'시 ' + str(check_date_min) + '분은 확인 가능하지 않습니다'
        next_hour = check_date_hour
        next_min = check_date_min
        current_date = check_date.replace('-', '')

    # print(room_status)                    # debug
    format_date = current_date[:4] + '년 ' + current_date[4:6] + '월 ' + current_date[6:] + '일 '
    format_time = str(next_hour) + '시 ' + str(next_min) + '분'

    # Not reserve-able time
    if not (6<=next_hour<=23):
        print('it is not possible to reserve or check empty rooms at current time')
        return format_date + format_time +'은 예약 가능한 시간이 아닙니다'

    # calculate next reserveable time
    next_hour_str = '0'+str(next_hour) if next_hour<10 else str(next_hour)
    next_min_str = '0'+str(next_min) if next_min<10 else str(next_min)
    reserve_time = current_date + next_hour_str + next_min_str
    # print(reserve_time)   # for debug
    
    threads = []
    results = []
    room_status = [None] * len(room_numbers)
    for i, room_no in enumerate(room_numbers):
        # multiprocessing
        result = mp.Array('i', [i, False], lock=False)  # boolean data is in interform, need to typecase later
        # session = self.session_pool[i]
        p = mp.Process(target=is_room_empty, args=(room_no, reserve_time, result))
        p.start()
        sleep(0.1) # taking a break before each request acually increases performance
        threads.append(p)
        results.append(result)
    for p in threads:
        p.join()
    
    for r in results:
        room_status[r[0]] = bool(r[1])

    room_status_string = ''
    empty_room_starting_ment = format_date + ' ' + format_time + '에 비어있는 상상랩은:\n'
    for i, r in enumerate(room_status):
        room_name = '상상랩'
        if room_numbers[i] == 98:
            room_name = 'Coding Talk'
        if r == True:
            if room_status_string != '':
                room_status_string += '\n'
            room_status_string += room_name + (str(i+1) if room_numbers[i]!=98 else '')
        
    if room_status_string == '':
        return format_date + ' ' + format_time + '에는 모든 방이 예약 되어있습니다'
    return empty_room_starting_ment + room_status_string


def get_detailed_room_info(room_no:str, check_date:str=''):
    year, month, day = check_date.split('-')
    heading_text = f'{year}년 {month}월 {day}일 상상랩{room_no}번 예약 가능 시간대:\n'

    # assumes valid date
    room_no = room_numbers[int(room_no)-1]
    response = requests.get(String.URL.ROOM_T.value + str(room_no) + String.URL.ROOM_T_date_p.value + check_date)
    # soup = BeautifulSoup(response.text, 'html.parser')

    # '06:00-06:15', '06:15-06:30' ... '23:30-23:45', '23:45-24:00'
    # '06:00', '06:15' ... '23:30', '23:45'
    times = []
    for i in range(6,24):
        for j in range(0,60,15):
                times.append(f'{i:02d}:{j:02d}') # -{i if j<45 else i+1:02d}:{j+15 if j<45 else 0:02d}')
    times_dict = dict.fromkeys(times, "o")
    start_idx = 0
    if not check_date:
        check_date = datetime.now().strftime('%Y-%m-%d')
    
    # get available time data
    while True:
        search_text = "ViewInfo('" + check_date + "','"

        found_idx = response.text.find(search_text, start_idx)

        if found_idx == -1:
            break
        start_idx = found_idx +len(search_text)
        search_idx = found_idx +len(search_text)
        
        # print(response.text[search_idx:search_idx+11])
        time_str_start, time_str_end = response.text[search_idx:search_idx+11].split("','")
        time_str_start = time_str_start[:2] + ':' + time_str_start[2:]
        time_str_end = time_str_end[:2] + ':' + time_str_end[2:]

        keys = times_dict.keys()
        start = False
        for k in keys:
            if k == time_str_start:
                start = True
            if k == time_str_end:   # end time is not inclusive
                break
            if start:
                times_dict[k] = 'x'

    # only return future values
    if check_date == datetime.now().strftime('%Y-%m-%d'):   # today
        # if the check date is same as today, there should be past times
        now = datetime.now()                # server's current time
        current_hour = now.hour
        current_min = now.minute
        next_hour = current_hour
        if current_min < 15:
            next_min = 15
        elif current_min < 30:
            next_min = 30
        elif current_min < 45:
            next_min = 45
        else:
            next_min = 0
            next_hour = current_hour+1
        
        if (next_hour > 6) or (next_hour == 6 and next_min > 0):
            next_time_text = str(next_hour) + ':' + str(next_min) # excluding this value remove all previous ones
            for key in times_dict.keys():
                if key != next_time_text:
                    times_dict[key] = '-'
                else:
                    break
    
    # 06:00-06:15   o
    # 06:15-06:30   x
    return_string = ''
    time_block = False

    print(times_dict)
    for key in times_dict.keys():
        if times_dict[key] == '-':
            continue

        if time_block == False:
            if times_dict[key] == 'o':
                return_string += '\n'
                return_string += key + ' ~ '
                time_block = True
        elif time_block == True:
            if times_dict[key] == 'o':
                if key == '23:45':
                    return_string += '24:00'
                continue
            elif times_dict[key] == 'x':
                return_string += key
                time_block = False
    
    return heading_text + return_string


def time_taken():
    t1 = datetime.now()
    result = get_current_empty_room()
    t2 = datetime.now()
    print('total time consumed: ' + str(t2-t1))
    return result


def apply_room(user_data, room_data) -> bool:
    # room_apply_heading = 
    copy_room_apply_heading = copy.deepcopy(room_apply_heading)
    print('user_data: ', user_data)
    print('room_data: ', room_data)
    copy_room_apply_heading['Cookie'] = 'PHPSESSID=' + user_data['session']

    # copy_room_apply_payload = copy.deepcopy(room_apply_payload)

    r = requests.post(String.URL.ROOM_APPLY.value, data=room_data, headers=copy_room_apply_heading)

    if '예약신청이 완료되었습니다' in r.text:
        return True
    else:
        print('상상랩 예약 신청에 실패했습니다')
        print(r.text)
        return False

if __name__ == '__main__':
    print(time_taken())