from bot.bot_interpreter import QQMessage
import bot.bot_interpreter as interpreter
from torn import APICenter
import threading
from fuzzywuzzy import process
from utils import utils
import xlrd
import os


CURRENT_OS_PATH = os.path.split(os.path.realpath(__file__))[0]
# 初始化
item_nickname_map = {}
wb = xlrd.open_workbook(os.path.join(CURRENT_OS_PATH, 'items.xls'))
sheet = wb.sheet_by_name('items')
for row_idx in range(1, sheet.nrows):
	row_values = sheet.row_values(row_idx, start_colx=1, end_colx=None)
	name = row_values[0].lower()

	should_skip = False
	skips = ['unknown', 'undefined']
	for skip in skips:
		if name.startswith(skip):
			should_skip = True
			break
	if not name:
		should_skip = True
	if should_skip:
		continue

	nicknames = [x.lower() for x in row_values[1].split(',') if x]
	nicknames.insert(0, name)
	for nickname in nicknames:
		if item_nickname_map.get(nickname):
			raise Exception('重复别名%s' % nickname)
		item_nickname_map[nickname] = row_idx


# --*-- 汇总 --*-- #
def query_bazaar_by_nickname(msg: QQMessage):
	message = msg.message
	to_match = message[message.find('#')+1:]
	if len(to_match) == 0:
		interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='商品名不能为空'))
		return

	match_list = process.extractBests(to_match, item_nickname_map.keys())
	match_name_list = [m[0] for m in match_list]
	confidences_list = [m[1] for m in match_list]
	reply = ''
	if confidences_list[0] > 60:
		# 置信度大于60
		match_name = match_name_list[0]
		reply += match_name + '\n'
		item_id = item_nickname_map[match_name]
		item_list = APICenter.query_bazaar_item(item_id)

		if len(item_list) == 0:
			reply += '市场上没有该商品\n'
		for item in item_list[:5]:
			reply += '价格:%s, 数量:%d\n' % (utils.number_to_format_str(item[0]), item[1])

		maybe = []
		for match_name, confidence in match_list[1:4]:
			if confidence > 60 and item_nickname_map[match_name] != item_id and item_nickname_map[match_name] not in [item_nickname_map[may_name] for may_name in maybe]:
				maybe.append(match_name)
		if maybe:
			print(maybe)
			reply += '您可能要查找: %s' % '、'.join(maybe)
		else:
			reply = reply[:-1]

	else:
		maybe = []
		for match_name, confidence in match_list[:4]:
			if confidence > 60 and item_nickname_map[match_name] not in [item_nickname_map[may_name] for may_name in maybe]:
				maybe.append(match_name)
		if maybe:
			print(maybe)
			reply += '您可能要查找: %s' % '、'.join(maybe)
	if len(reply) == 0:
		reply = '查无结果'
	interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=reply))
	return


def query_pointsmarket(msg: QQMessage):
	reply = ''
	item_list = APICenter.query_pointsmarket()
	if len(item_list) > 0:
		reply += '当前Points价格:\n'
		for cost, quantity in item_list:
			reply += '价格:%d 数量%d\n' % (cost, quantity)
		reply = reply[:-1]
	else:
		reply = '查询出错'
	image_path = utils.text_to_image(reply)
	interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=reply, image_path=image_path))
	return


# --*-- 接口 --*-- #
bazaar_query_commands = {
	'ba#': query_bazaar_by_nickname,
	'pt#': query_pointsmarket
}

bazaar_query_commands_description = {
	'ba#': 'ba#[物品名] 查询bazaar的商品',
	'pt#': '查询point市场'
}

#
def solve_description():
	return bazaar_query_commands_description


def solve_test(msg: QQMessage):
	message = msg.message
	for command in bazaar_query_commands.keys():
		if message.startswith(command):
			return bazaar_query_commands.get(command)


def solve(msg: QQMessage):
	if solve_test(msg):
		thread = threading.Thread(target=solve_test(msg), args=(msg,))
		thread.start()

if __name__ == '__main__':
	print(type(bazaar_query_commands))
