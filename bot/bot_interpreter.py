import nonebot
import bot.BOT_CONFIG as config
import GLOBAL_CONFIG
import threading
import time
import re


# --*-- 公共接口 --*--
class QQMessage:
    def __init__(self, message="", group_number=0, sender_nickname="",
                 sender_number=0, sender_group_card='', image_path=''):
        super(QQMessage, self).__init__()
        self.message = message
        self.image_path = image_path
        self.group_number = group_number
        self.sender_nickname = sender_nickname
        self.sender_number = sender_number
        self.sender_group_card = sender_group_card

    def parse_none_bot_message(self, msg):
        self.__init__()
        self.message = str(msg['message'])
        self.sender_nickname = str(msg['sender']['nickname'])
        self.sender_number = int(msg['sender']['user_id'])

        try:
            self.group_number = int(msg['group_id'])
            self.sender_group_card = str(msg['sender']['card'])
            if self.sender_group_card == '':
                self.sender_group_card = self.sender_nickname
        except Exception as e:
            self.group_number = 0
            self.sender_group_card = self.sender_nickname
            print('私聊消息')


plugin_list = []
group_card_list = []


def register_plugin(plugin):
    plugin_list.append(plugin)


# 启动消息监听
def commence_life_cycle():
    thread = threading.Thread(target=nonebot.run)
    thread.start()


is_suspended = False


# 消息监听
def receive_msg(message: QQMessage):
    global is_suspended
    # su指令
    if message.sender_number in GLOBAL_CONFIG.super_user:
        msg = message.message
        if msg == 'bot挂起':
            send_msg(QQMessage(sender_number=message.sender_number, group_number=message.group_number,
                               message='啊 我被挂起了'))
            is_suspended = True
        elif msg == 'bot恢复':
            is_suspended = False
            send_msg(QQMessage(sender_number=message.sender_number, group_number=message.group_number,
                               message='恢复正常工作'))
        elif msg == 'bot状态':
            tmp_is_suspended = is_suspended
            is_suspended = False
            send_msg(QQMessage(sender_number=message.sender_number, group_number=message.group_number,
                               message='挂起' if tmp_is_suspended else '正常'))
            is_suspended = tmp_is_suspended

    if is_suspended:
        return

    if message.group_number != 0 and message.group_number not in GLOBAL_CONFIG.available_groups:
        return

    if message.message in ['帮助', '手册', '说明']:
        all_solve_list = []
        for plugin in plugin_list:
            first = True
            plugin_description = plugin.solve_description()
            for command in plugin_description.keys():
                message.message = command
                if plugin.solve_test(message):
                    if first:
                        # all_solve_list.append('-')
                        first = False
                    all_solve_list.append('%s : %s' % (command, plugin_description[command]))
        send_msg(QQMessage(group_number=message.group_number, sender_number=message.sender_number,
                           message='\n'.join(all_solve_list)))
    elif message.message in ['财富密码']:
        sender_card = message.sender_group_card
        r = re.search('([0-9]{6,})', sender_card)
        if r:
            torn_number = r.group(1)
            send_msg(QQMessage(group_number=message.group_number, message='%s 财富密码为%s' % (sender_card, torn_number)))
        else:
            send_msg(QQMessage(group_number=message.group_number, message='%s 财富密码识别失败' % sender_card))
    else:
        for plugin in plugin_list:
            if plugin.solve_test(message):
                plugin.solve(message)
                break


# 发送消息
def send_msg(message: QQMessage):
    if is_suspended:
        return
    message_sender(message)


# 设置群昵称后缀 前缀为iTorn
def set_group_card_suffix(group_number: int, suffix: str):
    set_group_card(group_number, '[红笔高价收购花花玩偶]' + suffix)


# 设置群昵称
def set_group_card(group_number: int, group_card: str):
    group_card_list.append({'group_number':group_number, 'group_card':group_card})


# --*-- none_bot --*--
nonebot.init(config)
bot = nonebot.get_bot()
send_queue = []


# 消息监听
@bot.on_message()
async def message_listener(m):
    print(m)
    message = QQMessage()
    message.parse_none_bot_message(m)
    receive_msg(message)


# 消息发送
def message_sender(message):
    send_queue.append(message)


# 防止消息发送过快
@nonebot.scheduler.scheduled_job('interval', seconds=1)
async def none_bot_work_queue():
    # 修改群名片
    if len(group_card_list) > 0:
        group_card_obj = group_card_list.pop(0)
        group_number = group_card_obj['group_number']
        group_card = group_card_obj['group_card']
        self_number = (await bot.get_login_info())['user_id']
        if self_number > 0:
            await bot.set_group_card(group_id=int(group_number), user_id=self_number, card=str(group_card))

    # 发送消息或图片
    qq_message = None
    if len(send_queue) > 0:
        qq_message = send_queue.pop(0)
    if not qq_message:
        return
    group_number = int(qq_message.group_number)
    sender_number = int(qq_message.sender_number)
    msg = str(qq_message.message)
    image_path = str(qq_message.image_path)
    # 发送图片
    if image_path:
        if group_number == 0:
            await bot.send_private_msg(user_id=sender_number, message="[CQ:image,file=%s]" % image_path)
        else:
            await bot.send_group_msg(group_id=group_number, message="[CQ:image,file=%s]" % image_path)
        return
    # 消息长度大于140可能会出问题 切割一下
    leap = GLOBAL_CONFIG.REPLY_MESSAGE_SLICE_LEN
    msg_slices = [msg[i:i+leap] for i in range(0, len(msg), leap)] if (leap > 0) else [msg]
    if group_number == 0:
        for msg_slice in msg_slices:
            await bot.send_private_msg(user_id=sender_number, message=msg_slice)
    else:
        for msg_slice in msg_slices:
            await bot.send_group_msg(group_id=group_number, message=msg_slice)


if __name__ == '__main__':
    commence_life_cycle()
    time.sleep(3)
    send_msg(QQMessage(group_number=1124031768, message="test"))
