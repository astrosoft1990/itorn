import requests
import threading, time
import GLOBAL_CONFIG
DEBUG_LOG = False

API_KEY = GLOBAL_CONFIG.GET_API_KEY()
API_FACTION_ID = "36134"
API_CHAIN_REQUEST_URL = "https://api.torn.com/faction/%s?selections=chain,timestamp&key=%s" % (API_FACTION_ID, API_KEY)
API_FACTION_REQUEST_URL = "https://api.torn.com/faction/%s?selections=&key=%s" % (API_FACTION_ID, API_KEY)
API_REQUEST_TIME_INTERVAL = 5

session = requests.session()
if GLOBAL_CONFIG.USE_PROXIES:
    session.proxies = GLOBAL_CONFIG.proxies

faction_name = ""
chain_current = -1
chain_max = -1
chain_timeout = -1
chain_last_update_timestamp = -1


def debug_log_chain_state():
    if DEBUG_LOG:
        print(chain_current, chain_max, chain_timeout)


def chain_detail_info_make() -> str:
    return 'faction: %s\n当前chain: %d\n最大chain: %d\n剩余时间: %d秒\n预估剩余时间:%d秒\n距离上次更新已过去:%d秒' % (faction_name, chain_current, chain_max, chain_timeout, (chain_timeout - (time.time()-chain_last_update_timestamp)), time.time()-chain_last_update_timestamp)


def chain_simple_info_make() -> str:
    return '当前chain: %d\n最大chain: %d\n预估剩余时间:%d' % ( chain_current, chain_max,  (chain_timeout - (time.time()-chain_last_update_timestamp)))


def update_faction_state():
    global faction_name
    r = requests.get(API_FACTION_REQUEST_URL).json()
    try:
        faction_name = r["name"]
    except Exception as e:
        faction_name = ""


def update_chain_state():
    global  chain_current, chain_max, chain_timeout, chain_last_update_timestamp
    r = session.get(API_CHAIN_REQUEST_URL).json()
    try:
        chain_current =  r["chain"]["current"]
        chain_max = r["chain"]["max"]
        chain_timeout = r["chain"]["timeout"]
        chain_last_update_timestamp = r["timestamp"]

    except Exception as e:
        chain_current = -1
        chain_max = -1
        chain_timeout = -1
        chain_last_update_timestamp = -1


def query_bazaar_item(item_id: int) -> list:
    API_BAZZAR_REQUEST_URL = 'https://api.torn.com/market/%d?selections=&key=%s' % (item_id, API_KEY)
    items = requests.get(API_BAZZAR_REQUEST_URL).json()['bazaar']
    ret = []
    if items:
        for item in items:
            ret.append((item['cost'], item['quantity']))
    return ret


def query_pointsmarket() -> list:
    API_BAZZAR_REQUEST_URL = 'https://api.torn.com/market/?selections=pointsmarket&key=%s' % API_KEY
    points_info = requests.get(API_BAZZAR_REQUEST_URL).json()['pointsmarket']
    ret = []
    if points_info:
        for _, item in points_info.items():
            ret.append((item['cost'], item['quantity']))
    ret.sort(key=lambda x:x[0])
    return ret


def api_life_cycle():
    while 1:
        try:
            if faction_name == "":
                update_faction_state()
            update_chain_state()
            debug_log_chain_state()
        except Exception as e:
            print(e)
        print('api.center.heartbeat')
        time.sleep(API_REQUEST_TIME_INTERVAL)


def commence_life_cycle():
    # 不要多次调用
    thread = threading.Thread(target=api_life_cycle)
    thread.start()

if __name__ == '__main__':
    query_bazaar_item(203)