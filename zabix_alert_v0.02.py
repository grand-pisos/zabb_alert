import time
import requests
import datetime
import os

print('zabix_alert_v0.02' + '\n')

#исключения по триггерам
black_list = [
    'workly_device_status',
    'Disk I/O is overloaded on uatdb.av.ru',
    'AZV-> Service Level less than 60%',
    'AV.RU-> Отслеживание сервиса привязки телефона, количество ошибок',
    'Статус регистраторов Workly'
]

# доступы записаны в переменной ОС
bot_token = os.getenv('b_token')
bot_chatID = os.getenv('b_chatID')
send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text='

ZABBIX_API_URL  = os.getenv('z_url') + 'api_jsonrpc.php'

def bot_message(text):
    tget = send_text + str(text)
    return tget

def post_api(json):
    rq = requests.post(ZABBIX_API_URL, json=json)
    return rq

log_in = {
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "user": os.getenv('z_user'),
        "password": os.getenv('z_pass')
    },
    "id": 1
}

r = post_api(log_in)

# получение токена
AUTHTOKEN = r.json()['result']
print('Successful authorization')

# формирование параметров запроса с начальной точкой времени
def getnew(time):
    get = {
        "jsonrpc": "2.0",
        "method": "alert.get",
        "params": {
            "limit": "30",
            "time_from": time,
            "sortfield": 'eventid',
            "sortorder": "DESC"
        },
        "id": 2,
        "auth": AUTHTOKEN
    }
    return get

now = datetime.datetime.now()
lasttime = int(now.timestamp()) - 86400  


res = post_api(getnew(lasttime))
lastevent = res.json()['result'][0]['eventid']
print('Successful request')

# запись последних отправленных триггеров
send = []
for i in res.json()['result']:
    if i['eventid'] not in send:
        send.append(i['eventid'])

sc = 0

while True:
    if len(send) > 40: 
        del send[0:10]
    if sc > 2:
        os.system('cls')
        sc = 0
    call = post_api(getnew(lasttime))
    al = []
    for i in call.json()['result']:
        if i['eventid'] not in al:
            al.append(i['eventid']) # получение данных из последнего запроса (al - новые алерты, send - уже отправленные) 
    if call.json()['result'][0]['eventid'] == lastevent:
        print('Search...')
        time.sleep(3)
        print('[|||______]')
        time.sleep(3)
        print('[||||||___]')
        time.sleep(3)
        print('[|||||||||]')
        time.sleep(1)
        sc += 1
        continue
    else:
        lastevent = call.json()['result'][0]['eventid']
        for i in al[::-1]:  # проверка - был ли отправлен триггер
            if i in send:
                continue
            else:
                send.append(i)
                for j in call.json()['result']:
                    if j['eventid'] == i:
                        d = {}
                        d[j['eventid']] = j['subject'] + ' ' + j['message']  # тело триггера
                        if j['subject'] not in black_list:
                            response = requests.get(bot_message(d.get(i)))
                            print('Message sent')
                        else:
                            print('pass')
                            continue
