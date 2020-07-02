from bot.bot_interpreter import QQMessage
import bot.bot_interpreter as interpreter
import plugin.stockQuery.arson_warehouse_spider as spider
from plugin.stockQuery.foreign_item_map import *
import threading, random, re, time
import inspect
import ctypes
import GLOBAL_CONFIG

# 激活spider
spider_thread = spider.commence_life_cycle()


def _async_raise(tid, exctype):
	"""raises the exception, performs cleanup if needed"""
	tid = ctypes.c_long(tid)
	if not inspect.isclass(exctype):
		exctype = type(exctype)
	res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
	if res == 0:
		raise ValueError("invalid thread id")
	elif res != 1:
		# """if it returns a number greater than one, you're in trouble,
		# and you should call it again with exc=NULL to revert the effect"""
		ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
		raise SystemError("PyThreadState_SetAsyncExc failed")


def restart_spider(msg: QQMessage):
	sender_number = msg.sender_number
	if sender_number not in GLOBAL_CONFIG.super_user:
		return

	interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='正在重启库存'))
	global spider_thread
	if spider_thread.is_alive():
		_async_raise(spider_thread.ident, SystemExit)
		spider_thread = spider.commence_life_cycle()
		interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='强制退出并重启'))
	else:
		spider_thread = spider.commence_life_cycle()
		interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='已重启'))


# --*-- 接口 --*-- #
def get_country_by_nickname(nickname):
	for k, v in country_nickname_map.items():
		if nickname in v:
			return k


def search_flower_plushie_for(msg: QQMessage):
	if not spider_thread.is_alive():
		interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='库存查询已停止,请联系管理员'))
		return

	message = msg.message
	nickname = message[message.find('#') + 1:].lower()
	country = get_country_by_nickname(nickname)

	countries = []
	if country:
		countries = [country]
	else:
		countries = country_nickname_map.keys()

	target_ids = []
	for item_ids in [country_flower_plushie_map.get(country) for country in countries]:
		for item_id in item_ids:
			target_ids.append(item_id)

	target_dict = {}
	for item in spider.foreign_item_list:
		if item.item_id in target_ids:
			# FIXME: xanax的id有几个重复 要判断是不是南非的
			if item.item_id == 206 and item.country != 'South Africa':
				pass
			else:
				if target_dict.get(item.country):
					target_dict[item.country].append(item)
				else:
					target_dict[item.country] = [item]

	if not target_dict:
		interpreter.send_msg(QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message='查询出错'))
	else:
		ret_message = ''
		if not country:
			ret_message += '本地更新时间: %s\n' % spider.last_update_date
		for country, items in target_dict.items():
			country_name = country_name_map[country]
			ret_message += "%s" % country_name
			if len(country_name) < 3:
				ret_message += '\t'
			ret_message += ':'
			for item in items:
				ret_message += "  %s%d" % (item_name_map[item.item_id], item.stock)
			ret_message += '\n'
		interpreter.send_msg(
			QQMessage(group_number=msg.group_number, sender_number=msg.sender_number, message=ret_message[:-1]))
	return


# --*-- 接口 --*-- #
stock_query_commands = {
	'ff#': search_flower_plushie_for,
	'重启库存': restart_spider
}

stock_query_commands_description = {
	'ff#': 'ff#[国家] 查询对应国家的飞花库存 留空则返回所有国家数据'
}


#
def solve_description():
	return stock_query_commands_description


def solve_test(msg: QQMessage):
	message = msg.message.lower()
	for command in stock_query_commands.keys():
		if message.startswith(command):
			return stock_query_commands.get(command)


def solve(msg: QQMessage):
	if solve_test(msg):
		thread = threading.Thread(target=solve_test(msg), args=(msg,))
		thread.start()


if __name__ == '__main__':
	content = '[TTT]Mirrorr[2564936]'
	result = re.search('.*?([a-zA-Z0-9]*?)\[.*?', content)
	print(result.group())
	pass
