import sqlite3
import datetime
import time

class DBManager:

    BanUsers = {}
    ApiKeys = {}

    def clearTimeoutItems(self):
        tmpArray = {}
        for k, v in self.BanUsers.items():
            if v['timeout'] > datetime.datetime.now():
                tmpArray[k] = v
        self.BanUsers = tmpArray

    def changeUserBan(self, uid, isBan, level, expires, reason = None):
        if level == None:
            if isnull:
                level = 0
            else:
                level = result[0][0]
        self.BanUsers[uid] = {
                'uid': uid,
                'ban': isBan,
                'reason': reason,
                'level': level,
                'expires': expires,
                'timeout': datetime.datetime.now() + datetime.timedelta(minutes=15)
            }
        if isBan == True:
            isBan = '0'
        elif isBan == False:
            isBan = '1'
        else:
            raise TypeError('isBan must be boolean')
        groupConfigDB = sqlite3.connect('ban-users.db')
        c = groupConfigDB.cursor()
        try:
            c.execute('SELECT Level FROM BanUsers WHERE UserID = ?', (uid,))
            result = c.fetchall()
            isnull = len(result) == 0
        except sqlite3.OperationalError:    
            c.execute('CREATE TABLE BanUsers (UserID INT NOT NULL, Ban INT2 NOT NULL, Reason TEXT, `Level` INTEGER NOT NULL DEFAULT 0, `Expires` INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(`UserID`))')
        if isnull:
            if reason != None:
                c.execute('INSERT INTO BanUsers (UserID, Ban, Level, Expires, Reason) VALUES (?,?,?,?,?)', (uid, isBan, level, expires, reason))
            else:
                c.execute('INSERT INTO BanUsers (UserID, Ban, Level, Expires) VALUES (?,?,?,?)', (uid, isBan, level, expires))
        else:
            if reason != None:
                c.execute('UPDATE BanUsers SET Ban = ?, Level = ?, Expires = ?, Reason = ? WHERE UserID = ?', (isBan, level, expires, reason, uid))
            else:
                c.execute('UPDATE BanUsers SET Ban = ?, Level = ?, Expires = ? WHERE UserID = ?', (isBan, level, expires, uid))
        groupConfigDB.commit()
        groupConfigDB.close()
    
    def getUserBan(self, uid):
        try:
            gc = self.BanUsers[uid]
            if gc['timeout'] > datetime.datetime.now():
                return gc
        except KeyError:
            pass
        groupConfigDB = sqlite3.connect('ban-users.db')
        c = groupConfigDB.cursor()
        try:
            c.execute('SELECT UserID, Ban, Reason, Level, Expires FROM BanUsers WHERE UserID = ?', (uid,))
        except sqlite3.OperationalError:
            c.execute('CREATE TABLE BanUsers (UserID INT PIRMARY NOT NULL, Ban INT2 NOT NULL, Reason TEXT NOT NULL, Level INT2 NOT NULL, Expires INT NOT NULL)')
        data = c.fetchall()
        if len(data) == 0:
            data = {
                'uid': uid,
                'ban': False,
                'reason': None,
                'level': 1,
                'expires': -1,
                'timeout': datetime.datetime.now() + datetime.timedelta(minutes=15)
            }
            self.BanUsers[uid] = data
            return data
        if self.__getIsExpires(data[0][4]):
            c.execute('DELETE FROM BanUsers WHERE UserID = ?', (i[0],))
            groupConfigDB.commit()
            groupConfigDB.close()
            data = {
                'uid': uid,
                'ban': False,
                'reason': None,
                'level': 1,
                'expires': -1,
                'timeout': datetime.datetime.now() + datetime.timedelta(minutes=15)
            }
            self.BanUsers[uid] = data
            return data
        groupConfigDB.close()
        data = {
            'uid': data[0][0],
            'ban': data[0][1] == 0,
            'reason': data[0][2],
            'level': data[0][3],
            'expires': data[0][4],
            'timeout': datetime.datetime.now() + datetime.timedelta(minutes=15)
        }
        self.BanUsers[uid] = data
        return data

    def __getIsExpires(self, expires_time):
        if expires_time == 0:
            return False
        if expires_time <= time.time():
            return True

    def get_all_ban(self):
        groupConfigDB = sqlite3.connect('ban-users.db')
        c = groupConfigDB.cursor()
        try:
            c.execute('SELECT UserID, Ban, Level, Expires,  Reason FROM BanUsers')
        except sqlite3.OperationalError:
            c.execute('CREATE TABLE BanUsers (UserID INT PIRMARY NOT NULL, Ban INT2 NOT NULL, Reason TEXT NOT NULL)')
        data = c.fetchall()
        groupConfigDB.close()
        if len(data) == 0:
            return []
        real_data = []
        for i in data:
            real_data.append(
                {
                    'uid': i[0],
                    'ban': i[1] == 0,
                    'level': i[2],
                    'expires': i[3],
                    'reason': i[4]
                }
            )
        return real_data

    def getApiKeyStatus(self, key):
        try:
            gc = self.ApiKeys[key]
            if gc['timeout'] > datetime.datetime.now():
                return gc
        except KeyError:
            pass
        groupConfigDB = sqlite3.connect('api-keys.db')
        c = groupConfigDB.cursor()
        try:
            c.execute('SELECT KeyID, Key, Query, SetValue, Limited, Admin, PostAPI, Note FROM ApiKeys WHERE Key = ?', (key,))
        except sqlite3.OperationalError:
            c.execute('CREATE TABLE `ApiKeys` (`KeyID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Key` VARCHAR(64) NOT NULL UNIQUE, `Query` INT2 NOT NULL, `SetValue` INT2 NOT NULL, `Limited` INT2 NOT NULL, `Admin` INT2 NOT NULL, `Note` TEXT);')
        data = c.fetchall()
        if len(data) == 0:
            data = {
                'key_id': -1,
                'key': key,
                'query': False,
                'setValue': False,
                'limited': False,
                'admin': False,
                'post_api': False,
                'note': None,
                'indb': False,
                'timeout': datetime.datetime.now()
            }
            self.ApiKeys[key] = data
            groupConfigDB.close()
            return data
        groupConfigDB.close()
        data = {
            'key_id': data[0][0],
            'key': data[0][1],
            'query': data[0][2] == 0,
            'setValue': data[0][3] == 0,
            'limited': data[0][4] == 0,
            'admin': data[0][5] == 0,
            'post_api': data[0][6] == 0,
            'note': data[0][7],
            'indb': True,
            'timeout': datetime.datetime.now() + datetime.timedelta(minutes=15)
        }
        return data

    def addApiKey(self, key, query = True, setValue = False, limited = True, admin = False, post_api = False, note = None):
        self.BanUsers[key] = {
            'key': key,
            'query': query,
            'setValue': setValue,
            'limited': limited,
            'admin': admin,
            'note': note,
            'indb': True,
            'timeout': datetime.datetime.now() + datetime.timedelta(minutes=15)
        }
        if query == True:
            query = '0'
        elif query == False:
            query = '1'
        else:
            raise TypeError('query must be boolean')
        if setValue == True:
            setValue = '0'
        elif setValue == False:
            setValue = '1'
        else:
            raise TypeError('setValue must be boolean')
        if limited == True:
            limited = '0'
        elif limited == False:
            limited = '1'
        else:
            raise TypeError('limited must be boolean')
        if admin == True:
            admin = '0'
        elif admin == False:
            admin = '1'
        else:
            raise TypeError('admin must be boolean')
        if post_api == True:
            post_api = '0'
        elif post_api == False:
            post_api = '1'
        else:
            raise TypeError('post_api must be boolean')
        groupConfigDB = sqlite3.connect('api-keys.db')
        c = groupConfigDB.cursor()
        try:
            c.execute('SELECT Key FROM ApiKeys WHERE Key = ?', (key,))
        except sqlite3.OperationalError:
            c.execute('CREATE TABLE `ApiKeys` (`KeyID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `Key` VARCHAR(64) NOT NULL UNIQUE, `Query` INT2 NOT NULL, `SetValue` INT2 NOT NULL, `Limited` INT2 NOT NULL, `Admin` INT2 NOT NULL, `Note` TEXT);')
        have_rows = len(c.fetchall()) == 0
        c.close()
        c = groupConfigDB.cursor()
        if have_rows:
            if note != None:
                c.execute('INSERT INTO ApiKeys (Key, Query, SetValue, Limited, Admin, PostAPI, Note) VALUES (?,?,?,?,?,?,?)', (key, query, setValue, limited, admin, post_api, note))
            else:
                c.execute('INSERT INTO ApiKeys (Key, Query, SetValue, Limited, Admin, PostAPI) VALUES (?,?,?,?,?)', (key, query, setValue, limited, admin, post_api))
        else:
            if note != None:
                c.execute('UPDATE ApiKeys SET Query = ?, SetValue = ?, Limited = ?, admin = ?, PostAPI = ?, Note = ? WHERE Key = ?', (query, setValue, limited, admin, post_api, note, key))
            else:
                c.execute('UPDATE ApiKeys SET Query = ?, SetValue = ?, Limited = ?, admin = ?, PostAPI = ? WHERE Key = ?', (query, setValue, limited, admin, post_api, key))
        groupConfigDB.commit()
        groupConfigDB.close()
