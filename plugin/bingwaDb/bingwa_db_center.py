import pymssql
import numpy as np
import matplotlib
import time, random, threading
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot,savefig
import matplotlib.ticker as mtick
from DBUtils.PooledDB import PooledDB

SERVER_HOST = '10.93.134.153'
SERVER_PORT = 1433
SERVER_USERNAME = 'torn'
SERVER_PASSWORD = 'torn1'

DATABASE_NAME = 'TornCity'

TMP_DIRECTORY= 'tmp/'

PLOTING_LOCK = threading.Lock()

pool = PooledDB(pymssql, 5, host=SERVER_HOST, port=SERVER_PORT, user=SERVER_USERNAME, password=SERVER_PASSWORD, database=DATABASE_NAME, charset="utf8")

def unique_string() -> str:
    return "%s_%s" % (str(time.time()), str(random.randint(1000, 100000)))

def test_log_all_columns():
    conn = pool.connection()
    cursor = conn.cursor()

    cursor.execute("exec sp_columns TornBingWaAllData;")
    rows = cursor.fetchall()
    for row in rows:
        print(row[3])

    cursor.close()
    conn.close()


def query_for_information(key: str, player_id: str) -> list:
    conn = pool.connection()
    cursor = conn.cursor()

    cursor.execute("exec TornQQBotFunctionV3 '%s','%s'" % (str(key), str(player_id)))
    rows = cursor.fetchall()[::-1]

    return rows

def query_for_all_key() -> list:
    conn = pool.connection()
    cursor = conn.cursor()

    cursor.execute("select name from syscolumns where id=object_id('TornBingWaAllData')")
    rows = cursor.fetchall()
    print([x[0] for x in  rows])
    return rows

def query_for_monthly_rank(key: str, faction_key: str) -> list:
    conn = pool.connection()
    cursor = conn.cursor()

    cursor.execute("exec TornQQBotFunctionRank '%s','%s'" % (str(key), str(faction_key)))
    rows = cursor.fetchall()

    return rows

def query_for_weekly_rank(key: str, faction_key: str) -> list:
    conn = pool.connection()
    cursor = conn.cursor()

    cursor.execute("exec TornQQBotWeekRank '%s','%s'" % (str(key), str(faction_key)))
    rows = cursor.fetchall()

    return rows

def query_for_daily_rank(key: str, faction_key: str) -> list:
    conn = pool.connection()
    cursor = conn.cursor()

    cursor.execute("exec TornQQBotDayRank '%s','%s'" % (str(key), str(faction_key)))
    rows = cursor.fetchall()

    return rows
