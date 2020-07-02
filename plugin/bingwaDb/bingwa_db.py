from bot.bot_interpreter import QQMessage
import bot.bot_interpreter as interpreter
from plugin.bingwaDb import bingwa_db_center
import threading
from prettytable import PrettyTable
from utils import utils

# --*-- 汇总 --*-- #
def query_for_all_information_key(msg: QQMessage):
    key_list = [x[0] for x in bingwa_db_center.query_for_all_key()]
    text = '\n'.join(key_list)
    image_path = utils.text_to_image(text)
    interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, image_path=image_path))


def query_for_all_special_key(msg: QQMessage):
    key_list = ['fly', 'win', 'lost' 'jail' 'hosp', 'xan', 'networth', 'point', 'Mug', 'bs', 'od', 'lsd', 'extt']
    text = ', '.join(key_list)
    interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=text))


def query_for_information(msg: QQMessage):
    sender_card = msg.sender_group_card
    message = msg.message

    main_message = message[message.find('#')+1:]
    key, torn_number = main_message.split('#')
    try:
        torn_number = str(int(torn_number))
        if torn_number == '0':
            torn_number = utils.split_torn_numner(sender_card)
        else:
            sender_card = torn_number
    except Exception as e:
        torn_number = utils.split_torn_numner(sender_card)


    if torn_number == '0' and False:
        interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='财富密码识别失败'))
    else:
        rows = bingwa_db_center.query_for_information(key, torn_number)
        reply = ''
        if len(rows) <= 0:
            reply ='查询出错了'
        else:
            trans_date = [row[0] for row in rows]
            data = [row[1] for row in rows]
            function_type = rows[0][2]
            if trans_date[0].lower() == 'list':
                reply = '请使用更详细的关键字查询: %s' % (', '.join(data))
            elif trans_date[0].lower() == 'error':
                reply = data[0]
            else:
                reply = '%s\n' % sender_card
                reply += '查询参数: %s\n' % function_type
                reply += '当前: %s\n' % utils.number_to_format_str(data[-1])
                if len(data) > 1:
                    data_steps = [data[i] - data[i-1] for i in range(1, len(data))]
                    reply += "增量: %s" % utils.number_to_format_str(data_steps[0])
                    for step in data_steps[1:]:
                        reply += ' -> %s' % utils.number_to_format_str(step)
                    reply += '\n'

                    reply += '平均: %s' % utils.number_to_format_str(sum(data_steps) / len(data_steps))

        interpreter.send_msg(
                QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=reply))


def query_for_monthly_rank(msg: QQMessage):
    message = msg.message
    query_key = None
    query_faction_key = None
    try:
        _, query_key, query_faction_key = message.split('#')
        if len(query_faction_key) == 0:
            query_faction_key = 0
        else:
            query_faction_key = int(query_faction_key)
        if query_faction_key < 0:
            raise Exception('rank faction 参数错误')
        query_faction_key = str(query_faction_key)
    except Exception as e:
        print('rank 拆分参数出错')
        interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='拆分参数出错'))
        return

    rows = bingwa_db_center.query_for_monthly_rank(query_key, query_faction_key)

    if len(rows) <= 0:
        interpreter.send_msg(
            QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='查询出错了'))
    elif len(rows) == 1 and rows[0][1] == 2509529 and rows[0][-1] == 0:
        interpreter.send_msg(
            QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=rows[0][-2]))
    else:
        tb = PrettyTable()
        tb.field_names = ['RankID', 'player_id', 'name', 'Faction', 'Data']
        for row in rows:
            row = [x for x in row]
            row[-1] = utils.number_to_format_str(row[-1])
            tb.add_row(row)
        interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, image_path=utils.text_to_image('月报查询:%s  faction:%s\n' % (query_key, query_faction_key) + str(tb))))



def query_for_weekly_rank(msg: QQMessage):
    message = msg.message
    query_key = None
    query_faction_key = None
    try:
        _, query_key, query_faction_key = message.split('#')
        if len(query_faction_key) == 0:
            query_faction_key = 0
        else:
            query_faction_key = int(query_faction_key)
        if query_faction_key < 0:
            raise Exception('rank faction 参数错误')
        query_faction_key = str(query_faction_key)
    except Exception as e:
        print('rank 拆分参数出错')
        interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='拆分参数出错'))
        return

    rows = bingwa_db_center.query_for_weekly_rank(query_key, query_faction_key)

    if len(rows) <= 0:
        interpreter.send_msg(
            QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='查询出错了'))
    elif len(rows) == 1 and rows[0][1] == 2509529 and rows[0][-1] == 0:
        interpreter.send_msg(
            QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=rows[0][-2]))
    else:
        tb = PrettyTable()
        tb.field_names = ['RankID', 'player_id', 'name', 'Faction', 'Data']
        for row in rows:
            row = [x for x in row]
            row[-1] = utils.number_to_format_str(row[-1])
            tb.add_row(row)
        interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, image_path=utils.text_to_image('周报查询:%s  faction:%s\n' % (query_key, query_faction_key) + str(tb))))


def query_for_daily_rank(msg: QQMessage):
    message = msg.message
    query_key = None
    query_faction_key = None
    try:
        _, query_key, query_faction_key = message.split('#')
        if len(query_faction_key) == 0:
            query_faction_key = 0
        else:
            query_faction_key = int(query_faction_key)
        if query_faction_key < 0:
            raise Exception('rank faction 参数错误')
        query_faction_key = str(query_faction_key)
    except Exception as e:
        print('rank 拆分参数出错')
        interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='拆分参数出错'))
        return

    rows = bingwa_db_center.query_for_daily_rank(query_key, query_faction_key)

    if len(rows) <= 0:
        interpreter.send_msg(
            QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='查询出错了'))
    elif len(rows) == 1 and rows[0][1] == 2509529 and rows[0][-1] == 0:
        interpreter.send_msg(
            QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=rows[0][-2]))
    else:
        tb = PrettyTable()
        tb.field_names = ['RankID', 'player_id', 'name', 'Faction', 'Data']
        for row in rows:
            row = [x for x in row]
            row[-1] = utils.number_to_format_str(row[-1])
            tb.add_row(row)
        interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, image_path=utils.text_to_image('日报查询:%s  faction:%s\n' % (query_key, query_faction_key) + str(tb))))



# --*-- 接口 --*-- #
bingwa_db_commands = {
    '信息#': query_for_information,
    '月报#': query_for_monthly_rank,
    '周报#': query_for_weekly_rank,
    '日报#': query_for_daily_rank,
    '所有参数#': query_for_all_information_key,
    '特殊参数#': query_for_all_special_key
}

bingwa_db_commands_description = {
    '信息#': '信息#[关键字]#[id]查询数据,id留空则查询财富密码',
    '月报#': '月报#[关键字]#[faction_type(0-9)] 查询排名, faction_type 1-8代表不同的帮派(待确定), 0为smth,sh,三体, 9为所有',
    '周报#': '~',
    '日报#': '~',
    '所有参数#': '查询所有参数',
    '特殊参数#': '查询特殊参数',
}

#
def solve_description():
    return bingwa_db_commands_description


def solve_test(msg: QQMessage):
    message = msg.message.lower()
    command = message
    for command in bingwa_db_commands.keys():
        if message.startswith(command):
            return bingwa_db_commands.get(command)


def solve(msg: QQMessage):
    if solve_test(msg):
        thread = threading.Thread(target=solve_test(msg), args=(msg,))
        thread.start()

