#!/usr/bin/python3

import datetime
import json
import dbmanager
import postapimgr
import time
from flask import Flask
from flask import request

banDB = dbmanager.DBManager()

def getReturnJson(uid, ban, level, expires, reason = None):
    py_array = {'ok': True, 'uid': str(uid), 'ban': ban, 'level': level, 'expires': expires}
    if reason != None:
        py_array['reason'] = reason
    return json.dumps(py_array)

print('Starting API server...\n')

apikey_get_all_count = {}
today_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))


def check_time():
    global today_time
    now_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    if today_time != now_time:
        apikey_get_all_count = {}
        today_time = now_time

app = Flask(__name__)
@app.route('/spamcheckerapi', methods = ['GET', 'POST'])
def TG_BOT():
    apikey = request.values.get("apikey", "__invalid__")
    method = request.values.get("method", "query")
    if apikey == '__invalid__':
        return '{"ok": false, "message": "Invalid API KEY"}'
    apiKeyStatus = banDB.getApiKeyStatus(apikey)
    if apiKeyStatus['indb'] == False:
        return '{"ok": false, "message": "Invalid API KEY"}'
    if method == 'query':
        # Query ban status
        if apiKeyStatus['query'] == False:
            return '{"ok": false, "message": "Permission denied"}'
        uid = request.values.get("uid", "__invalid__")
        try:
            int(uid)
        except Exception:
            return '{"ok": false, "message": "Invalid User ID"}'
        ban = banDB.getUserBan(uid)
        return getReturnJson(uid, ban['ban'], ban['level'], ban['expires'], ban['reason'])
    if method == 'get_all':
        # Query ban status
        if apiKeyStatus['query'] == False:
            return '{"ok": false, "message": "Permission denied"}'
        if apiKeyStatus['post_api'] == False:
            return '{"ok": false, "message": "Permission denied"}'
        check_time()
        try:
            my = apikey_get_all_count[apiKeyStatus['key_id']]
            if my >= 30:
                return '{"ok": false, "message": "Permission denied"}'
        except KeyError:
            apikey_get_all_count[apiKeyStatus['key_id']] = 0
            my = 0
        apikey_get_all_count[apiKeyStatus['key_id']] = my + 1
        return json.dumps({'ok': True, 'result': banDB.get_all_ban()})
    elif method == 'set_value':
        # Change ban status
        if apiKeyStatus['setValue'] == False:
            return '{"ok": false, "message": "Permission denied"}'
        uid = request.values.get("uid", "__invalid__")
        ban = request.values.get("ban", "__invalid__").lower()
        level = request.values.get("level", "__invalid__")
        expires = request.values.get("expires", "__invalid__")
        reason = request.values.get("reason", None)
        try:
            int(uid)
        except Exception:
            return '{"ok": false, "message": "Invalid User ID"}'
        try:
            int(level)
        except Exception:
            return '{"ok": false, "message": "Invalid level"}'
        if ban == 'true':
            ban = True
        elif ban == 'false':
            ban = False
        else:
            return '{"ok": false, "message": "Ban must be true or false"}'
        postapimgr.new_ban(uid, ban, level, expires, reason)
        banDB.changeUserBan(uid, ban, level, expires, reason)
        return '{"ok": true, "message": "Change success"}'
    elif method == 'set_webhook':
        # Set webhook
        if apiKeyStatus['post_api'] == False:
            return '{"ok": false, "message": "Permission denied"}'
        post_url = request.values.get("post_url", "__invalid__")
        if post_url == '__invalid__':
            postapimgr.remove_post_task(apiKeyStatus['key_id'])
            return '{"ok": true, "message": "Deleted"}'
        postapimgr.add_post_task(apiKeyStatus['key_id'], post_url)
        return '{"ok": true, "message": "Change success"}'
    elif method == 'add_key':
        # Add API Key
        if apiKeyStatus['admin'] == False:
            return '{"ok": false, "message": "Permission denied"}'
        key = request.values.get("key", "__invalid__")
        query = request.values.get("query", "__invalid__")
        setValue = request.values.get("set_value", "__invalid__")
        limited = request.values.get("limited", "__invalid__")
        post_api = request.values.get("post_api", "__invalid__")
        admin = request.values.get("admin", "__invalid__")
        note = request.values.get("note", None)
        if key == '__invalid__':
            return '{"ok": false, "message": "Invalid key"}'
        if query == 'true':
            query = True
        elif query == 'false':
            query = False
        else:
            return '{"ok": false, "message": "query must be true or false"}'
        if setValue == 'true':
            setValue = True
        elif setValue == 'false':
            setValue = False
        else:
            return '{"ok": false, "message": "set_value must be true or false"}'
        if limited == 'true':
            limited = True
        elif limited == 'false':
            limited = False
        else:
            return '{"ok": false, "message": "limited must be true or false"}'
        if post_api == 'true':
            post_api = True
        elif post_api == 'false':
            post_api = False
        else:
            return '{"ok": false, "message": "post_api must be true or false"}'
        if admin == 'true':
            admin = True
        elif admin == 'false':
            admin = False
        else:
            return '{"ok": false, "message": "admin must be true or false"}'
        banDB.addApiKey(key, query, setValue, limited, admin, post_api, note)
        return '{"ok": true, "message": "Change success"}'
    return '{"ok": false, "message": "Invalid method", "methods": ["query", "set_value", "add_key", "set_webhook", "get_all"]}'

app.run(
    host = '127.0.0.1',
    port = 8082,
    threaded = True,
    debug = False
)
