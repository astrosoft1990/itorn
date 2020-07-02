from bot.bot_interpreter import QQMessage
import bot.bot_interpreter as interpreter
from torn import APICenter
from plugin.bingwaDb import bingwa_db_center
import threading, re
from utils import utils

# --*-- 汇总 --*-- #
def query_for_all_key(msg: QQMessage):
    key_list = [x[0] for x in bingwa_db_center.query_for_all_key()]
    text = '\n'.join(key_list)
    image_path = utils.text_to_image(text)
    interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, image_path=image_path))


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
                reply += '当前: %s\n' % utils.number_to_str(data[-1])
                if len(data) > 1:
                    data_steps = [data[i] - data[i-1] for i in range(1, len(data))]
                    reply += "增量: %s" % utils.number_to_str(data_steps[0])
                    for step in data_steps[1:]:
                        reply += ' -> %s' % utils.number_to_str(step)
                    reply += '\n'

                    reply += '平均: %s' % utils.number_to_str(sum(data_steps) / len(data_steps))

        interpreter.send_msg(
                QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=reply))

def query_for_rank(msg: QQMessage):
    sender_card = msg.sender_group_card
    message = msg.message
    main_message = message[message.find('#')+1:]
    key, torn_number = main_message.split('#')
    rows = bingwa_db_center.query_for_information(key)
    reply = ''
    if len(rows) <= 0:
        reply ='查询出错了'
    else:
        for row in rows
        reply += row
        reply += '\n'
    interpreter.send_msg(
            QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=reply))
# --*-- 接口 --*-- #
bingwa_db_commands = {
    '信息#': query_for_information,
    '排行#': query_for_rank,
    '所有参数#': query_for_all_key
}

bingwa_db_commands_description = {
    '信息#': '信息#[关键字]#[id]查询数据,id留空则查询财富密码',
    '所有参数#': '查询所有参数'
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

