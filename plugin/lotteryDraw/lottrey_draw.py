from bot.bot_interpreter import QQMessage
import bot.bot_interpreter as interpreter
import threading
import random
import os
import pickle
from utils import utils

# --*-- 汇总 --*-- #
class Lottery:
    def __init__(self, group_number=0, sponsor_number=0, sponsor_card='', award=''):
        super(Lottery, self).__init__()
        self.group_number = group_number
        self.sponsor_number = sponsor_number
        self.sponsor_card = sponsor_card
        self.award = award
        self.participants = []


class Participant:
    def __init__(self, participant_number, participant_card):
        super(Participant, self).__init__()
        self.participant_number = participant_number
        self.participant_card = participant_card


CURRENT_OS_PATH = os.path.split(os.path.realpath(__file__))[0]
SERIALIZE_PATH = 'lottery_list.txt'
lottery_list = []
rw_lock = threading.Lock()
with open(os.path.join(CURRENT_OS_PATH, SERIALIZE_PATH), 'a+') as fp:
    pass

with open(os.path.join(CURRENT_OS_PATH, SERIALIZE_PATH), 'rb') as fp:
    try:
        lottery_list = pickle.load(fp)
    except Exception as e:
        print(e)


def get_lottery_in_group(group_number: int) -> Lottery:
    for lottery in lottery_list:
        if lottery.group_number == group_number:
            return lottery


def start_new_lottery(msg: QQMessage):
    group_number = msg.group_number
    sponsor_group_card = msg.sender_group_card
    if get_lottery_in_group(group_number):
        interpreter.send_msg(QQMessage(group_number=group_number, message='群里已经有正在进行的抽奖了'))
    else:
        message = msg.message
        award = message[message.find('#') + 1:]
        sponsor_number = msg.sender_number
        sponsor_card = msg.sender_group_card
        with rw_lock, open(os.path.join(CURRENT_OS_PATH, SERIALIZE_PATH), 'wb+') as fp:
            lottery_list.append(Lottery(group_number=group_number, sponsor_number=sponsor_number, sponsor_card=sponsor_card, award=award))
            pickle.dump(lottery_list, fp)

        interpreter.set_group_card_suffix(group_number=group_number, suffix='[抽奖中]')
        interpreter.send_msg(QQMessage(group_number=group_number, message=sponsor_group_card + '开启了抽奖 奖品:' + award))


def abort_lottery(msg: QQMessage):
    group_number = msg.group_number
    sender_number = msg.sender_number
    lottery = get_lottery_in_group(group_number)
    if not lottery or lottery.sponsor_number != sender_number:
        return
    else:
        with rw_lock, open(os.path.join(CURRENT_OS_PATH, SERIALIZE_PATH), 'wb+') as fp:
            lottery_list.remove(lottery)
            pickle.dump(lottery_list, fp)
        interpreter.send_msg(QQMessage(group_number=group_number, message='抽奖中止了'))
        interpreter.set_group_card_suffix(group_number=group_number, suffix='[没有抽奖]')


def participate_in_lottery(msg: QQMessage):
    group_number = msg.group_number
    sender_number = msg.sender_number
    sender_group_card = msg.sender_group_card
    lottery = get_lottery_in_group(group_number)
    if not lottery:
        interpreter.send_msg(QQMessage(group_number=group_number, message='当前没有抽奖'))
        return
    else:
        if sender_number in [x.participant_number for x in lottery.participants]:
            interpreter.send_msg(QQMessage(sender_number=sender_number, message=sender_group_card + ': 您已参加\n[%s - %s]' % (lottery.sponsor_card, lottery.award)))
        else:
            participant = Participant(participant_number=sender_number, participant_card=sender_group_card)
            with rw_lock, open(os.path.join(CURRENT_OS_PATH, SERIALIZE_PATH), 'wb+') as fp:
                lottery.participants.append(participant)
                pickle.dump(lottery_list, fp)
            interpreter.send_msg(QQMessage(sender_number=sender_number, message=sender_group_card + ': 参加成功\n[%s - %s]' % (lottery.sponsor_card, lottery.award)))


def current_lottery_text(msg: QQMessage):
    current_lottery(msg, use_image=False)


def current_lottery(msg: QQMessage, use_image=True):
    group_number = msg.group_number
    lottery = get_lottery_in_group(group_number)
    if not lottery:
        interpreter.set_group_card_suffix(group_number=group_number, suffix='[没有抽奖]')
        interpreter.send_msg(QQMessage(group_number=group_number, message='当前没有抽奖'))
        return
    else:
        interpreter.set_group_card_suffix(group_number=group_number, suffix='[抽奖中]')
        reply = '现在正在进行的是\n由%s送出的%s的抽奖\n参与抽奖共计%d人:\n%s' % (lottery.sponsor_card, lottery.award, len(lottery.participants),
                                                        '\n'.join([participant.participant_card for participant in lottery.participants]))
        if use_image:
            interpreter.send_msg(QQMessage(group_number=group_number, image_path=utils.text_to_image(reply)))
        else:
            interpreter.send_msg(QQMessage(group_number=group_number, message=reply))


def end_lottery(msg: QQMessage):
    message = msg.message
    group_number = msg.group_number
    sender_number = msg.sender_number

    try:
        lucky_sum = int(message[message.find('#') + 1:])
        if lucky_sum <= 0:
            raise Exception
    except Exception as e:
        interpreter.send_msg(QQMessage(group_number=group_number, message='参数有误'))
        return

    lottery = get_lottery_in_group(group_number)
    if not lottery or lottery.sponsor_number != sender_number:
        return
    else:
        with rw_lock, open(os.path.join(CURRENT_OS_PATH, SERIALIZE_PATH), 'wb+') as fp:
            lottery_list.remove(lottery)
            pickle.dump(lottery_list, fp)

        participants = lottery.participants
        if len(participants) <= 0:
            interpreter.set_group_card_suffix(group_number=group_number, suffix='[没有抽奖]')
            interpreter.send_msg(QQMessage(group_number=group_number, message='参与人数不足,抽奖已结束'))
        else:
            lucky_list = []
            for idx in random.sample(range(0, len(participants)), min(lucky_sum, len(participants))):
                lucky_list.append(participants[idx])

            interpreter.set_group_card_suffix(group_number=group_number, suffix='[没有抽奖]')
            interpreter.send_msg(QQMessage(group_number=group_number, message='开奖结果:\n%s\n获得了%s送出的:%s' % (
                '\n'.join(["[CQ:at,qq=%s]" % participant.participant_number for participant in lucky_list]),
                lottery.sponsor_card, lottery.award)))
            for p in participants:
                interpreter.send_msg(QQMessage(sender_number=p.participant_number, message='开奖结果:\n%s\n获得了%s送出的:%s' % (
                    '\n'.join(["%s" % participant.participant_card for participant in lucky_list]),
                    lottery.sponsor_card, lottery.award)))


lottery_draw_detailed_commands_description = {
    '开启抽奖#': '开始抽奖#[奖品]',
    '开始抽奖#': '同开始抽奖#',
    '中止抽奖': '中止抽奖',
    '参加抽奖': '参加抽奖',
    '当前抽奖': '当前正在进行的抽奖的状态',
    '#当前抽奖': '当前抽奖文字版',
    '结束抽奖#': '结束抽奖#[开奖人数]'
}


def lottery_description(msg: QQMessage):
    all_solve_list = []
    for k, v in lottery_draw_detailed_commands_description.items():
        all_solve_list.append(k + ' : ' + v)
    interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='\n'.join(all_solve_list)))


# --*-- 接口 --*-- #
lottery_draw_commands = {
    '开启抽奖#': start_new_lottery,
    '开始抽奖#': start_new_lottery,
    '中止抽奖': abort_lottery,
    '参加抽奖': participate_in_lottery,
    '当前抽奖': current_lottery,
    '#当前抽奖': current_lottery_text,
    '结束抽奖#': end_lottery,
    '抽奖说明': lottery_description
}

lottery_draw_commands_description = {
    '抽奖说明': '输入抽奖说明查看详细说明',
}


#
def solve_description():
    return lottery_draw_commands_description


def solve_test(msg: QQMessage):
    message = msg.message
    group_number = msg.group_number
    if group_number == 0:
        return
    for command in lottery_draw_commands.keys():
        if message.startswith(command):
            return lottery_draw_commands.get(command)


def solve(msg: QQMessage):
    if solve_test(msg):
        thread = threading.Thread(target=solve_test(msg), args=(msg,))
        thread.start()
