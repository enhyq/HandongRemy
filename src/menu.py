import requests
import json

menu_url = 'http://smart.handong.edu/api/service/menu'

def get_menu_json_data():
    r = requests.get(menu_url)
    j = json.loads(r.text)
    return j

# if corner is specified, return only the corner's menu
def get_today_menu(corner:str=''):
    j = get_menu_json_data()
    
    haksik_data = j['haksik']
    haksik_headings = ['든든한동(아침)', '든든한동(점심)', '든든한동(저녁)', 'H-Plate', '', '그레이스 가든', '따스한동']
    haksik_string = ''

    corner_string_dictionary = {}
    
    for i, heading in enumerate(haksik_headings):
        if heading:
            if i:
                haksik_string += '\n ------------ \n'
            haksik_string += heading
            haksik_string += str(haksik_data[i]['menu_kor']).replace('\r\n', '\n 🍚 ').replace('-원산지: 메뉴게시판 참조-', '')
            corner_string_dictionary[heading] = heading + str(haksik_data[i]['menu_kor']).replace('\r\n', '\n 🍚 ').replace('-원산지: 메뉴게시판 참조-', '')
    haksik_string += '\n'

    moms_data = j['moms']   # this must be 'moms
    moms_headings = ['맘스 아침', '맘스 점심', '맘스 저녁']
    moms_string = ''
    for i, heading in enumerate(moms_headings):
        if heading:
            if i:
                moms_string += '\n ------------ \n'
            moms_string += heading
            moms_string += '\n 🍚 ' + str(moms_data[i]['menu_kor']).replace('\r\n', '\n 🍚 ')
            corner_string_dictionary[heading] = heading + '\n 🍚 ' + str(moms_data[i]['menu_kor']).replace('\r\n', '\n 🍚 ')
    composite_string = '<<<학식>>> \n' + haksik_string + '\n<<<맘스>>> \n' + moms_string
    
    corner_string_dictionary['든든한동'] = corner_string_dictionary['든든한동(아침)'] + '\n' + corner_string_dictionary['든든한동(점심)'] + '\n' + corner_string_dictionary['든든한동(저녁)']
    corner_string_dictionary['맘스'] = corner_string_dictionary['맘스 아침'] + '\n' + corner_string_dictionary['맘스 점심'] + '\n' + corner_string_dictionary['맘스 저녁']
    
    if corner:
        return corner_string_dictionary[corner]
    return composite_string