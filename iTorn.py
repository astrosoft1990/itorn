import threading, time
import bot.bot_interpreter as interpreter
from torn import APICenter
from plugin.chainGuard import chain_guard
from plugin.lotteryDraw import lottrey_draw
from plugin.stockQuery import stock_query
from plugin.personalStateQuery import personal_state_query
from plugin.bingwaDb import bingwa_db
from plugin.marketQuery import market_query

if __name__ == '__main__':
    thread = threading.Thread()
    thread.setDaemon(True)
    thread.start()

    interpreter.commence_life_cycle()
    APICenter.commence_life_cycle()

    # interpreter.register_plugin(chain_guard)
    interpreter.register_plugin(stock_query)
    interpreter.register_plugin(personal_state_query)
    interpreter.register_plugin(lottrey_draw)
    interpreter.register_plugin(bingwa_db)
    interpreter.register_plugin(market_query)