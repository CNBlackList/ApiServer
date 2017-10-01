import urllib.request, urllib.parse
import json

class MiniApi:

    ApiKey = ''
    ApiHost = ''

    PARSE_NONE = 0
    PARSE_MARKDOWN = 1
    PARSE_HTML = 2

    GroupAdminList = {}
    MyInfo = None

    __USER_AGENT = 'DogeFramework/1.0'

    def __init__(self, ApiKey, ApiHost = 'api.telegram.org'):
        self.ApiKey = ApiKey
        self.ApiHost = ApiHost

    def __tgapi_json(self, method, data = None):
        requestURL = 'https://' + self.ApiHost + '/bot' + self.ApiKey + '/' + method
        if data != None:
            postData = json.dumps(data).encode('utf-8')
        request = urllib.request.Request(requestURL)
        request.add_header('Content-Type', 'application/json; charset=utf-8')
        request.add_header('User-Agent', self.__USER_AGENT)
        try:
            if data == None:
                recMsg = urllib.request.urlopen(request)
            else:
                recMsg = urllib.request.urlopen(request, postData)
        except urllib.error.HTTPError as e:
            recMsg = e
        return {'code':recMsg.getcode(), 'content':recMsg.read().decode('utf-8')}

    def sendMessage(
        self,
        Message,
        ChatID,
        ReplyMessageID = None,
        ParseMode = 1,
        DisableWebPagePreview = True,
        DisableNotification = True,
        ReplyMarkup = None
        ):
        if type(ChatID) != int:
            raise TypeError('Reply ID must be int.')
        if type(DisableWebPagePreview) != bool:
            raise TypeError('DisableWebPagePreview ID must be bool.')
        if type(DisableNotification) != bool:
            raise TypeError('DisableWebPagePreview ID must be bool.')
        data = {
            'chat_id': str(ChatID),
            'text': str(Message),
            'disable_web_page_preview': str(DisableWebPagePreview),
            'disable_notification': str(DisableNotification)
            }
        if ReplyMessageID != None:
            if type(ReplyMessageID) == int:
                data['reply_to_message_id'] = ReplyMessageID
            else:
                raise TypeError('Reply ID must be int.')
        if ParseMode == self.PARSE_MARKDOWN:
            data['parse_mode'] = 'Markdown'
        elif ParseMode == self.PARSE_HTML:
            data['parse_mode'] = 'HTML'
        if ReplyMarkup != None:
            data['reply_markup'] = ReplyMarkup
        return self.__tgapi_json('sendMessage', data)['content']

api = MiniApi('123456789:asdfghjkl')