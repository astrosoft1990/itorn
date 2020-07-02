import random

__VERSION__ = "1.0.0"

# 是否启用代理
USE_PROXIES = True
proxies = {
	'http': '127.0.0.1:1080',
	'https': '127.0.0.1:1080'
}


# torn api key
API_KEY_POOL = ["701x8THpb8rKEvtc"]
GET_API_KEY = lambda: random.choice(API_KEY_POOL)


# 当回复消息大于该值时，会进行切割 0则不切割
REPLY_MESSAGE_SLICE_LEN = 300


# CQ的图片目录
CQ_DATA_IMAGE_PATH = r"C:\Users\Public\CQP\Pro\data\image"


# 监听的群
available_groups = [138838543, 1124031768, 460987951, 1083828784]


# 超级用户
super_user = [844912709, 30557398, 110445870]
