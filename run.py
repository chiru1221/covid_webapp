from flask import Flask, render_template, request, url_for, redirect
import datetime as dt
from datetime import datetime, date, timedelta
import requests
import subprocess
import json
import time
from sendmail import send
from operate_sql import write_db, read_user_action, read_user_name, read_ventilation_time, del_ventilation_time
import sendslack
app = Flask(__name__)
KIND_TO_JP = {
    'measure': '検温',
    'arrive': '手洗い',
    'homing': '帰宅'
}
JP_TO_KIND = {
    '検温': 'measure',
    '手洗い': 'arrive',
    '帰宅': 'homing'
}
with open('address.txt', 'r', encoding='utf-8') as f:
    To = f.readline().split('to:')[1].strip()
    From = f.readline().split('from:')[1].strip()
json_file = open('members.json', 'r', encoding='utf-8')
MEMBERS = json.load(json_file)
NAMES = list(MEMBERS.keys())

def report_db(date, name, kind, temp):
    if kind == 'measure':
        args = {
            'date': date,
            'day': date.date(),
            'name': name,
            'temp': temp
        }
        write_db('user_temp', args)
    
    args = {
        'date': date,
        'day': date.date(),
        'name': name,
        'action': KIND_TO_JP[kind]
    }
    return write_db('user_action', args)

def make_content(date, name, kind, temp):
    kind_jp = KIND_TO_JP[kind]
    contents = list()
    contents.append('{0}さん，{1}に{2}の報告が完了しました'.format(name, date.time().replace(microsecond=0), kind_jp))
    if kind == 'measure':
        contents.append('検温結果: {0}'.format(temp))

    return contents

def send_mail(date, name, kind, temp):
    title = 'コロナ対応のご報告'
    message = '名前: {0}\n日時: {1}\n時刻: {2}\n内容: '.format(name, date.date(), date.time().replace(microsecond=0))
    
    if kind == 'measure':
        title += '（検温）'
        message += '検温のご報告\n'
        message += '検温結果: {0}'.format(temp)
    elif kind == 'arrive':
        title += '（手洗い）'
        message += '研究室到着及び手洗いのご報告'
    else:
        title += '（帰宅）'
        message += '帰宅のご報告'

    return send(From, To, message, title)

def check_in_out(date, name, kind, temp):
    day = date.date()
    action_list = list(map(lambda x: JP_TO_KIND[x], read_user_action(name, day)))

    if action_list is None:
        return render_template('error.html', contents=['予期せぬエラーが発生しました．', 'お手数ですが，ご自身でご報告をお願いいたします．'])
    logs = [KIND_TO_JP[action] for action in action_list]
    if kind == 'measure':
        if len(action_list) == 0:
            return None
        elif action_list[-1] == 'homing':
            return None
        else:
            return render_template('check.html', content='既に検温の報告は完了しています．', link=False, logs=logs)
    elif kind == 'arrive':
        if len(action_list) != 0:
            if action_list[-1] == 'measure':
                return None
            elif action_list[-1] == 'arrive':
                return render_template('check.html', content='既に手洗いの報告は完了しています．', link=False, logs=logs)
            else:
                return render_template('check.html', content='検温の報告が完了していません．', link=True, logs=logs)
        else:
            return render_template('check.html', content='検温の報告が完了していません．', link=True, logs=logs)
    elif kind == 'homing':
        if len(action_list) != 0:
            if action_list[-1] == 'arrive':
                return None
            elif action_list[-1] == 'homing':
                return render_template('check.html', content='既に帰宅の報告は完了しています．', link=False, logs=logs)
            # else:
            #     return render_template('check.html', content='手洗いの報告が完了していません．', link=True, logs=logs)
        # else:
        #     return render_template('check.html', content='手洗いの報告が完了していません．', link=True, logs=logs)

# call after reporting database
def is_first(date, name, kind, temp):
    if kind != 'arrive':
        return 0
    day = date.date()
    in_list, _ = read_user_name(day)
    in_set = set(in_list)
    if len(in_set) == 1:
        return 1
    return 0

def is_last(date, name, kind, temp):
    if kind != 'homing':
        return 0
    day = date.date()
    in_list, out_list = read_user_name(day)
    in_set = set(in_list)
    out_set = set(out_list)

    # remove allnight(no homing)
    an_set = out_set - in_set
    for rm in an_set:
        out_set.remove(rm)
    
    if len(in_set) < 1:
        return 0
    elif len(out_set) < 1:
        return 0
    if len(in_set - out_set) == 0:
        return 1
    return 0

def is_rest(date):
    day = date.date()
    in_list, out_list = read_user_name(day)
    in_set = set(in_list)
    out_set = set(out_list)
    
    # remove allnight(no homing)
    an_set = out_set - in_set
    for rm in an_set:
        out_set.remove(rm)
    
    if len(in_set) < 1:
        return 0, 0

    if len(in_set - out_set) > 0:
        return 1, in_set - out_set
    return 0, 0

@app.route('/restcheck')
def rest_check():
    date = datetime.now()
    to_time = lambda ventil: dt.time(int(ventil.split(':')[0]), int(ventil.split(':')[1]))
    rest, in_set = is_rest(date)
    if rest:
        # report ventilation time
        ventils = read_ventilation_time(datetime.now().date())
        ventils = list(map(lambda x: ['{0}:{1}'.format(str(x_i.hour).zfill(2), str(x_i.minute).zfill(2)) for x_i in x], ventils))
        title = 'コロナ対応のご報告（換気時刻）'
        message = '本日({0})の換気時刻\n'.format(date.date())
        for ventil in ventils:
            message += '{0} - {1}\n'.format(to_time(ventil[0]), to_time(ventil[1]))
        send(From, To, message, title)
        contents = ['換気時刻を更新，及びメールを送信しました']
        # remind slack
        slack_message = "23:55での居残りを検知しました.\n帰宅報告漏れの場合は，日付時刻を修正し報告してください．\n<{0}>".format(request.url.rstrip('/restcheck'))
        for name in in_set:
            sendslack.send(MEMBERS[name], slack_message)
    
    return render_template('complete.html', contents=['ok'])

@app.route('/ventilation', methods=['GET'])
def ventilation_get():
    ventils = read_ventilation_time(datetime.now().date())
    ventils = list(map(lambda x: ['{0}:{1}'.format(str(x_i.hour).zfill(2), str(x_i.minute).zfill(2)) for x_i in x], ventils))
    return render_template('ventilation.html', title='Ventilation Time Management', ventils=ventils)

@app.route('/ventilation', methods=['POST'])
def ventilation_post():
    ventil_s = request.form.getlist('ventil_s')
    ventil_e = request.form.getlist('ventil_e')
    ventil_del = request.form.getlist('ventil_del')

    del_s, del_e = list(), list()
    for del_idx in ventil_del:
        del_idx = int(del_idx.split('_')[-1])
        del_s.append(ventil_s[del_idx])
        del_e.append(ventil_e[del_idx])
    for i in range(len(del_s)):
        ventil_s.remove(del_s[i])
        ventil_e.remove(del_e[i])
    ventil_s.remove('')
    ventil_e.remove('')
    
    to_time = lambda ventil: dt.time(int(ventil.split(':')[0]), int(ventil.split(':')[1]))
    date = datetime.now()
    args = {
        'date': date,
        'day': date.date(),
    }
    del_ventilation_time(date.date())
    for vs, ve in zip(ventil_s, ventil_e):
        args['ventil_s'] = to_time(vs)
        args['ventil_e'] = to_time(ve)
        write_db('ventil_time', args)
    contents = ['換気時刻を更新しました']
    
    if is_last(date, None, 'homing', None):
        title = 'コロナ対応のご報告（換気時刻）'
        message = '本日の換気時刻\n'
        for vs, ve in zip(ventil_s, ventil_e):
            message += '{0} - {1}\n'.format(to_time(vs), to_time(ve))

        send(From, To, message, title)
        contents = ['換気時刻を更新，及びメールを送信しました']
    return render_template('ventilation_complete.html', contents=contents)

@app.route('/', methods=['GET'])
def get():
    return render_template('index.html', title = 'COVID-19 Management', names=NAMES)

@app.route('/', methods=['POST'])
def post():
    name = request.form.get('name')
    kind = request.form.get('radAnswer')
    temp = request.form.get('temp')
    repair_time = request.form.get('time')
    repair_date = request.form.get('date')
    is_mail = request.form.get('is_mail')
    
    date = datetime.now()
    date_repair = False
    if repair_time != '':
        date = date.replace(hour=int(repair_time.split(':')[0]), minute=int(repair_time.split(':')[1]))
    if repair_date != '' and repair_date is not None:
        date = date.replace(month=int(repair_date.split('-')[1]), day=int(repair_date.split('-')[2]))
    
    args = {
        'date': date, 'name': name, 'kind': kind, 'temp': temp
    }

    check = check_in_out(**args)
    if check is not None:
        return check
        
    if is_mail is None:
        if send_mail(**args):
            contents = [
                'メール送信でエラーが生じました．',
                'お手数ですが，ご自身でご報告をお願いいたします．'
            ]
            return render_template('error.html', contents=contents)
    contents = make_content(**args)
    report_db(**args)

    if is_first(**args):
        requests.get('{0}remind'.format(request.url))

    sendslack.send(MEMBERS[name], contents[0].split('，')[-1])

    if is_last(**args):
        thre = dt.time(23, 55)
        if date.time() < thre:
            return redirect(url_for('ventilation_get'))
    
    return render_template('complete.html', contents=contents)

@app.route('/direct')
def simple():
    args = dict()
    for key in ['name', 'kind', 'temp']:
        args[key] = request.args.get(key)
    
    contents = None
    if args['name'] in NAMES:
        if args['kind'] in JP_TO_KIND.keys():
            kind = JP_TO_KIND[args['kind']]
            args['kind'] = kind
            if kind == 'measure':
                if args['temp'] is not None:
                    args['date'] = datetime.now()
                    contents = make_content(**args)
            else:
                args['date'] = datetime.now()
                contents = make_content(**args)
    
    if contents is None:
        contents = ['パラメータに誤りがあります.']
        return render_template('error.html', contents=contents)
    else:
        check = check_in_out(**args)
        if check is not None:
            return check
        
        if send_mail(**args):
            contents = [
                'メール送信でエラーが生じました．',
                'お手数ですが，ご自身でご報告をお願いいたします．'
            ]
            return render_template('error.html', contents=contents)
        contents = make_content(**args)
        report_db(**args)

        if is_first(**args):
            requests.get('{0}remind'.format(request.url))

        sendslack.send(MEMBERS[args['name']], contents[0].split('，')[-1])
        
        if is_last(**args):
            return redirect(url_for('ventilation_get'))
        
        return render_template('complete.html', contents=contents)

@app.route('/remind')
def remind():
    minutes = request.args.get('minutes')
    if minutes is None:
        minutes = 120
    else:
        try:
            minutes = int(minutes)
        except:
            minutes = 120

    date = datetime.now()
    args = {
        'date': date,
        'day': date.date(),
    }
    start = datetime.now() + timedelta(seconds=60 * minutes)
    args['ventil_s'] = start.time().replace(microsecond=0)
    args['ventil_e'] = (start + timedelta(seconds=60 * 10)).time().replace(microsecond=0)
    write_db('ventil_time', args)

    sendslack.send('#コロナ', 'reminder set in {0} minutes'.format(minutes))
    subprocess.run('at now + {0} minute -f call_reminder.sh'.format(minutes), shell=True, check=True)
    return render_template('remind.html', contents=['{0}分後にリマインダーを設定しました'.format(minutes)])


if __name__ == '__main__':
    json_file = open('server.json', 'r', encoding='utf-8')
    args = json.load(json_file)
    app.run(**args)
