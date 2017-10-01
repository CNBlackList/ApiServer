import urllib.request
import time
import _thread
import json
import traceback
import MiniAPI

POST_API_URL = 'http://cnblacklist-postapi-cnblacklist-postapi.a3c1.starter-us-west-1.openshiftapps.com/postapi'
POST_API_KEY = '0VjBHuQx9R3WosZ9KBC6pJuYtwoevjJT1KIIckTL'

def add_post_task(key_id, post_url):
    _thread.start_new_thread(
        http_post,
        (
            POST_API_URL,
            {'method': 'new_key', 'apikey': POST_API_KEY, 'keyid': key_id, 'post_url': post_url}
        )
    )

def remove_post_task(key_id):
    _thread.start_new_thread(
        http_post,
        (
            POST_API_URL,
            {'method': 'remove_key', 'apikey': POST_API_KEY, 'keyid': key_id}
        )
    )

def new_ban(uid, ban, level, expires, reason = None):
    if ban == True:
        ban = 'true'
    elif ban == False:
        ban = 'false'
    else:
        raise TypeError('WTF! WHAT! THE! FUCK!')
    _thread.start_new_thread(
        http_post,
        (
            POST_API_URL,
            {
                'method': 'new_ban',
                'apikey': POST_API_KEY,
                'uid': uid,
                'ban': ban,
                'level': level,
                'expires': expires,
                'reason': reason
            }
        )
    )


def http_post(url, data):
    post_data = urllib.parse.urlencode(data)
    post_data = post_data.encode('utf-8')
    request = urllib.request.Request(url)
    message_sended = False
    while True:
        try:
            data = urllib.request.urlopen(request, post_data, timeout = 10).read().decode('utf-8')
            result = json.loads(data)
            if result['ok'] == False:
                if message_sended == False:
                    MiniAPI.api.sendMessage('PostAPI 挂了: ValueError: ok=false\n\n```\n' + traceback.format_exc() + '```\n\n`' + data + '`', -1001072337178)
                    message_sended = True
                    time.sleep(60)
                    continue
            if message_sended:
                MiniAPI.api.sendMessage('PostAPI 恢复了', -1001072337178)
            return
        except Exception as e:
            if message_sended == False:
                MiniAPI.api.sendMessage('PostAPI 挂了:\n\n```\n' + traceback.format_exc() + '```', -1001072337178)
                message_sended = True
        time.sleep(60)
