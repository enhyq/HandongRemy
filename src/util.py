from cProfile import label
import copy
from flask import jsonify

# python copies by reference so using this variable in a function will modify it
response = {
        'version': '2.0',
        'template': {
            'outputs': [
                {
                    'simpleText': {
                        'text': ''
                    }
                }
            ]
        }
    }

# Kakao API response
def make_simple_text_json_response(text):
    copy_response = copy.deepcopy(response)
    copy_response['template']['outputs'][0]['simpleText']['text'] = text
    return jsonify(copy_response)

# messageText is same as label; action is type 'message'
def make_simple_text_json_response_with_quick_replies(text, label_list, message_list=[]):
    if not message_list:
        message_list = label_list
    
    copy_response = copy.deepcopy(response)
    copy_response['template']['outputs'][0]['simpleText']['text'] = text
    qrl = []
    for i in range(len(label_list)):
        qrl.append({
            "messageText": message_list[i],
            "action": "message",
            "label": label_list[i]
        })
    copy_response['template']['quickReplies'] = qrl
    return jsonify(copy_response)