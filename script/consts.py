# ------------------------ 字符串常量区------------------------- #
HOST = '0.0.0.0:80'  # 生产环境监听所有IP地址的80端口
TOKEN = 'xiexingyuan'  # 微信公众平台配置的Token

# ------------------------ 微信公众号配置 ------------------------ #
# 需要在微信公众平台获取
WECHAT_APPID = 'wxd40a2f1281ff19c6'  # 公众号AppID
WECHAT_APPSECRET = '100fe3e1f25cd963b70805f6c90eedd6'  # 公众号AppSecret

# ------------------------ 天气功能配置 ------------------------ #
# 和风天气API配置
WEATHER_API_KEY = '90c7e91d8a514d1bbdcbc9769a08ba7e'  # 天气API密钥
WEATHER_API_HOST = 'na5xmdv86m.re.qweatherapi.com'  # 和风天气API Host
WEATHER_DEFAULT_CITY = '101010100'  # 默认城市代码（北京）
WEATHER_API_TIMEOUT = 10  # API请求超时时间（秒）

# 天气API优先级配置（可以调整顺序）
# 'qweather' - 和风天气API（需要密钥）
# 'wttr' - wttr.in 免费API（无需密钥）
WEATHER_API_PRIORITY = ['qweather', 'wttr']

# 常用城市ID映射表（避免每次调用GEO API，提高响应速度）
WEATHER_CITY_ID_MAP = {
    '北京': '101010100',
    '上海': '101020100',
    '广州': '101280101',
    '深圳': '101280601',
    '杭州': '101210101',
    '成都': '101270101',
    '重庆': '101040100',
    '武汉': '101200101',
    '西安': '101110101',
    '南京': '101190101',
    '天津': '101030100',
    '苏州': '101190401',
    '长沙': '101250101',
    '郑州': '101180101',
    '青岛': '101120201',
    '大连': '101070201',
    '厦门': '101230201',
    '福州': '101230101',
    '济南': '101120101',
    '合肥': '101220101',
    '昆明': '101290101',
    '贵阳': '101260101',
    '南宁': '101300101',
    '海口': '101310101',
    '三亚': '101310201',
    '拉萨': '101140101',
    '乌鲁木齐': '101130101',
    '哈尔滨': '101050101',
    '长春': '101060101',
    '沈阳': '101070101',
    '石家庄': '101090101',
    '太原': '101100101',
    '呼和浩特': '101080101',
    '银川': '101170101',
    '兰州': '101160101',
    '西宁': '101150101',
    '南昌': '101240101',
    '无锡': '101190201',
    '宁波': '101210401',
    '东莞': '101281601',
    '佛山': '101280800',
    '温州': '101210701',
    '珠海': '101280701',
    '中山': '101281701',
    '惠州': '101280301',
    '常州': '101191101',
    '烟台': '101120501',
    '嘉兴': '101210301',
    '南通': '101190501',
    '金华': '101210901',
    '徐州': '101190801',
    '泉州': '101230501',
    '绍兴': '101210501',
    '台州': '101210601',
    '潍坊': '101120601',
    '洛阳': '101180901',
    '扬州': '101190601',
    '保定': '101090201',
    '唐山': '101090501',
    '镇江': '101190301',
    '湖州': '101210201',
    '芜湖': '101220301',
    '漳州': '101230601',
    '临沂': '101120901',
    '威海': '101121301',
    '邯郸': '101091001',
    '泰安': '101120801',
    '淮安': '101190901',
    '盐城': '101190701',
    '济宁': '101120701',
    '德州': '101120401',
    '聊城': '101121701',
    '枣庄': '101121401',
    '淄博': '101120301',
    '日照': '101121501',
    '泰州': '101191201',
    '宿迁': '101191301',
    '连云港': '101191001',
    '秦皇岛': '101091101',
    '廊坊': '101090601',
    '沧州': '101090701',
    '张家口': '101090301',
    '承德': '101090401',
    '邢台': '101090901',
    '衡水': '101090801',
    '阳泉': '101100301',
    '大同': '101100201',
    '朔州': '101100901',
    '晋城': '101100601',
    '晋中': '101100401',
    '运城': '101100701',
    '忻州': '101100501',
    '临汾': '101100801',
    '吕梁': '101101001',
    '包头': '101080201',
    '乌海': '101080301',
    '赤峰': '101080401',
    '通辽': '101080501',
    '鄂尔多斯': '101080701',
}

# 城市拼音映射表（用于wttr.in API）
WEATHER_CITY_PINYIN_MAP = {
    '北京': 'Beijing',
    '上海': 'Shanghai',
    '广州': 'Guangzhou',
    '深圳': 'Shenzhen',
    '杭州': 'Hangzhou',
    '成都': 'Chengdu',
    '重庆': 'Chongqing',
    '武汉': 'Wuhan',
    '西安': 'Xian',
    '南京': 'Nanjing',
    '天津': 'Tianjin',
    '苏州': 'Suzhou',
    '长沙': 'Changsha',
    '郑州': 'Zhengzhou',
    '青岛': 'Qingdao',
    '大连': 'Dalian',
    '厦门': 'Xiamen',
    '福州': 'Fuzhou',
    '济南': 'Jinan',
    '合肥': 'Hefei',
    '昆明': 'Kunming',
    '贵阳': 'Guiyang',
    '南宁': 'Nanning',
    '海口': 'Haikou',
    '三亚': 'Sanya',
    '拉萨': 'Lasa',
    '乌鲁木齐': 'Urumqi',
    '哈尔滨': 'Harbin',
    '长春': 'Changchun',
    '沈阳': 'Shenyang',
    '石家庄': 'Shijiazhuang',
    '太原': 'Taiyuan',
    '呼和浩特': 'Hohhot',
    '银川': 'Yinchuan',
    '兰州': 'Lanzhou',
    '西宁': 'Xining',
    '南昌': 'Nanchang',
    '无锡': 'Wuxi',
    '宁波': 'Ningbo',
    '东莞': 'Dongguan',
    '佛山': 'Foshan',
    '温州': 'Wenzhou',
    '珠海': 'Zhuhai',
    '中山': 'Zhongshan',
    '惠州': 'Huizhou',
}

# 暗号验证配置
SECRET_CODE = '源源爱娇娇'  # 暗号，用户发送此内容即可通过验证
SECRET_CODE_TIMEOUT = 300  # 暗号输入超时时间（秒），5分钟

# 暗号验证提示消息
SECRET_CODE_PROMPT = """🔐 身份验证

请在5分钟内输入暗号完成验证~

💡 提示：暗号是我们的专属口令哦！

⏰ 验证将在5分钟后自动取消"""

SECRET_CODE_WRONG = """❌ 暗号错误

您输入的暗号不正确，请重新输入~

💡 如果不知道暗号，可以联系我们获取哦！

⏰ 您还可以继续尝试"""

SECRET_CODE_EXPIRED = """⏰ 验证已过期

您的验证会话已超时，请重新发送「验证」开始验证~"""

# 取消验证
VERIFY_CANCELLED = """❌ 已取消验证

发送「验证」可以重新开始身份验证~"""

# 验证成功后的欢迎消息模板
VIP_WELCOME_MESSAGE = """🎊 恭喜！身份验证成功！

欢迎成为我们的VIP用户！
您的专属ID: {vip_id}
验证时间: {verify_time}

� 作为VIP用户，您将享有：
• 专属功能和服务
• 优先消息回复
• 更多精彩内容

感谢您的支持！💕"""

# 已验证用户的提示
ALREADY_VIP_MESSAGE = """😊 您已经是VIP用户啦！

您的专属ID: {vip_id}
验证时间: {verify_time}

无需重复验证哦~"""

WELCOM_MESSAGE = """�🎉 欢迎关注源源和娇娇的家！

感谢您的关注，这里是源源和娇娇分享生活点滴的温馨小窝~

🏠 在这里您可以：
• 了解我们的日常生活
• 分享有趣的话题
• 获取最新的动态更新

💬 您可以随时发送消息与我们互动，我们会尽快回复！

🔐 发送暗号可以解锁VIP身份哦~

回复"帮助"查看更多功能介绍"""


# ------------------------ 枚举类区------------------------ #
class WeChatMsgType:
    TEXT = 'text'
    IMAGE = 'image'
    LOCATION = 'location'
    EVENT = 'event'


# ------------------------ 命令关键词配置 ------------------------ #
class Commands:
    """用户命令关键词配置"""

    # 验证相关关键词
    VERIFY_KEYWORDS = ('验证', '身份验证', 'vip', '认证')

    # 帮助菜单关键词
    HELP_KEYWORDS = ('帮助', 'help', '?', '？')

    # 签到积分相关关键词
    CHECKIN_KEYWORDS = ('签到', '打卡')
    POINTS_KEYWORDS = ('积分', '我的积分', '查积分')
    RANKING_KEYWORDS = ('积分排行', '排行榜', '积分榜')
    CHECKIN_HELP_KEYWORDS = ('签到说明', '签到规则', '积分说明')

    # 昵称相关关键词
    SET_NICKNAME_KEYWORDS = ('设置昵称', '修改昵称', '改名', '改昵称')
    MY_NICKNAME_KEYWORDS = ('我的昵称', '查看昵称')

    # 菜谱功能关键词
    RECIPE_MENU = '菜谱'
    RECIPE_VIEW_LIST = '查看菜谱'
    RECIPE_ADD = '记录菜谱'
    RECIPE_ADD_PREFIX = '记录菜谱 '  # 快捷记录菜谱前缀，如 "记录菜谱 红烧肉"
    RECIPE_RANDOM = '随机菜谱'
    RECIPE_DETAIL_PREFIX = '菜谱 '  # 菜谱详情前缀，如 "菜谱 1"

    # VIP信息查询关键词
    VIP_INFO_KEYWORD = '我的vip'

    # 问候语关键词
    GREETING_KEYWORDS = ('你好', 'hello')

    # 取消/退出关键词
    CANCEL_KEYWORDS = ('取消', '退出', '返回')

    # 天气功能关键词
    WEATHER_KEYWORDS = ('天气', '今日天气', '查天气', '天气预报')
    WEATHER_PREFIX = '天气 '  # 查询指定城市天气，如 "天气 上海"
    WEATHER_CHANGE_CITY = ('更换城市', '切换城市', '换城市', '修改城市')  # 更换天气城市


class WeatherPushCommands:
    """天气推送订阅相关命令"""

    SUBSCRIBE = ('订阅天气', '订阅天气推送', '开启天气推送')
    UNSUBSCRIBE = ('取消订阅天气', '关闭天气推送', '取消天气推送')
    STATUS = ('天气推送状态', '我的天气订阅')


class RecipeCategory:
    """菜谱分类"""

    MEAT = 'meat'  # 荤菜
    VEGETABLE = 'veg'  # 素菜

    # 分类关键词映射
    MEAT_KEYWORDS = ('荤', '荤菜', '1', '肉')
    VEG_KEYWORDS = ('素', '素菜', '2', '蔬菜')

    # 分类显示名称
    DISPLAY_NAMES = {
        MEAT: '🥩 荤菜',
        VEGETABLE: '🥬 素菜',
    }

    @classmethod
    def get_category_by_keyword(cls, keyword):
        """根据关键词获取分类"""
        keyword = keyword.strip().lower()
        if keyword in cls.MEAT_KEYWORDS:
            return cls.MEAT
        elif keyword in cls.VEG_KEYWORDS:
            return cls.VEGETABLE
        return None

    @classmethod
    def get_display_name(cls, category):
        """获取分类的显示名称"""
        return cls.DISPLAY_NAMES.get(category, '未分类')


class WeChatEventType:
    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'


class UserStatus:
    """用户状态枚举"""

    NORMAL = 'normal'  # 普通用户
    VIP = 'vip'  # VIP用户（已通过暗号验证）


# ------------------------ 用户会话状态 ------------------------ #
class SessionState:
    """用户会话状态"""

    NONE = 'none'  # 无特殊状态
    WAITING_VERIFY = 'waiting_verify'  # 等待输入暗号验证
    WAITING_RECIPE = 'waiting_recipe'  # 等待输入菜谱内容
    WAITING_RECIPE_CATEGORY = 'waiting_recipe_category'  # 等待选择菜谱分类
    WAITING_WEATHER_CITY = 'waiting_weather_city'  # 等待设置天气城市
    WAITING_NICKNAME = 'waiting_nickname'  # 等待设置昵称


# ------------------------ 菜谱功能相关消息 ------------------------ #
# 一级帮助菜单
HELP_MESSAGE = """📖 功能列表

🤖 【AI对话】直接发送任意消息即可与AI聊天
1️⃣ 发送「签到」- 每日签到领积分
2️⃣ 发送「积分」- 查看我的积分
3️⃣ 发送「排行榜」- 积分排行榜
4️⃣ 发送「设置昵称」- 设置个性化昵称
5️⃣ 发送「天气」- 查看今日天气
6️⃣ 发送「菜谱」- 菜谱功能菜单
7️⃣ 发送「随机菜谱」- 今天吃什么
8️⃣ 发送「验证」- 身份验证成为VIP
9️⃣ 发送「我的VIP」- 查看VIP信息

💡 发送「新对话」可重置AI对话
💡 VIP用户签到积分翻倍！
💡 发送「天气 城市名」可查询指定城市"""

# 二级菜谱菜单
RECIPE_MENU_MESSAGE = """🍳 菜谱功能

1️⃣ 发送「查看菜谱」- 查看菜谱列表
2️⃣ 发送「记录菜谱」- 记录新菜谱（VIP专属）
3️⃣ 发送「随机菜谱」- 随便吃点啥

💡 发送「帮助」返回上级菜单"""

# 记录菜谱提示
RECIPE_INPUT_PROMPT = """📝 记录菜谱

请发送菜谱内容~
可以简单发个菜名，也可以详细写：
菜名/用料/做法

发送「取消」退出记录模式"""

# 记录菜谱成功
RECIPE_ADD_SUCCESS = """✅ 菜谱记录成功！

📝 {recipe_name}

已记录到菜谱列表~"""

# 取消记录菜谱
RECIPE_INPUT_CANCELLED = """❌ 已取消记录菜谱

发送「菜谱」返回菜谱功能菜单"""

# 非VIP用户尝试记录菜谱
RECIPE_VIP_ONLY = """😢 记录菜谱是VIP专属功能哦~

发送「验证」进行身份验证，成为VIP后即可使用！"""

# 菜谱列表为空
RECIPE_LIST_EMPTY = """📖 菜谱列表

暂时还没有菜谱哦~

VIP用户可以发送「记录菜谱」来添加第一个菜谱！"""

# 菜谱列表模板（分类展示）
RECIPE_LIST_TEMPLATE = """📖 菜谱列表

🥩 荤菜
{meat_list}

🥬 素菜
{veg_list}

共 {total} 个菜谱
发送「菜谱 序号」查看详情"""

# 菜谱分类为空提示
RECIPE_CATEGORY_LIST_EMPTY = """（暂无）"""

# 菜谱详情模板
RECIPE_DETAIL_TEMPLATE = """🍳 {recipe_name}

{recipe_content}

📅 记录时间：{create_time}
👤 记录者：{creator}"""

# 随机菜谱
RANDOM_RECIPE_TEMPLATE = """🎲 今天吃这个！

🍳 {recipe_name}

{recipe_content}

不满意？再发「随机菜谱」换一个~"""

# 随机菜谱 - 列表为空
RANDOM_RECIPE_EMPTY = """🎲 随机菜谱

暂时还没有菜谱哦~
VIP用户可以发送「记录菜谱」来添加菜谱！"""

# 菜谱序号无效
RECIPE_INDEX_INVALID = """❌ 菜谱序号无效

请发送「查看菜谱」查看菜谱列表，确认正确的序号~"""

# 新菜谱通知（附加在其他回复后面）
NEW_RECIPE_NOTIFICATION = """

---
📢 有 {count} 个新菜谱更新！发送「查看菜谱」查看~"""

# 菜谱记录失败
RECIPE_ADD_FAILED = """❌ 菜谱记录失败，请稍后重试~"""

# 菜谱分类选择提示
RECIPE_CATEGORY_PROMPT = """📝 已收到菜谱：{recipe_name}

请选择菜谱分类：
1️⃣ 荤菜 - 回复「荤」或「1」
2️⃣ 素菜 - 回复「素」或「2」

发送「取消」退出记录"""

# 菜谱分类无效
RECIPE_CATEGORY_INVALID = """❌ 分类无效

请回复：
1️⃣ 荤菜 - 回复「荤」或「1」
2️⃣ 素菜 - 回复「素」或「2」

发送「取消」退出记录"""

# 记录菜谱成功（带分类）
RECIPE_ADD_SUCCESS_WITH_CATEGORY = """✅ 菜谱记录成功！

📝 {recipe_name}
📂 分类：{category}

已记录到菜谱列表~"""

# 随机菜谱（一荤一素）
RANDOM_RECIPE_PAIR_TEMPLATE = """🎲 今天就吃这个！

{meat_section}

{veg_section}

不满意？再发「随机菜谱」换一组~"""

# 随机菜谱 - 荤菜部分
RANDOM_RECIPE_MEAT_SECTION = """🥩 荤菜：{recipe_name}
{recipe_content}"""

# 随机菜谱 - 素菜部分
RANDOM_RECIPE_VEG_SECTION = """🥬 素菜：{recipe_name}
{recipe_content}"""

# 随机菜谱 - 某分类为空
RANDOM_RECIPE_CATEGORY_EMPTY = """（暂无{category}菜谱）"""

# 随机菜谱 - 所有分类都为空
RANDOM_RECIPE_ALL_EMPTY = """🎲 随机菜谱

暂时还没有菜谱哦~
VIP用户可以发送「记录菜谱」来添加菜谱！"""

# ------------------------ VIP相关消息 ------------------------ #
# VIP信息查看
VIP_INFO_MESSAGE = """🌟 您的VIP信息

专属ID: {vip_id}
验证时间: {verify_time}
状态: {status}

感谢您的支持！💕"""

# 非VIP用户提示
NOT_VIP_MESSAGE = """😢 您还不是VIP用户

发送「验证」开始身份验证，输入暗号即可成为VIP！

成为VIP后可享受专属功能和服务哦~"""

# ------------------------ 通用回复消息 ------------------------ #
# 打招呼回复
HELLO_REPLY = """{vip_prefix}你好！很高兴为您服务！发送「帮助」查看功能列表~"""

# 默认回复
DEFAULT_REPLY = """{vip_prefix}感谢您的消息！发送「帮助」查看功能列表~"""

# VIP前缀
VIP_PREFIX = """【VIP专属】"""

# 图片消息回复
IMAGE_REPLY = """收到您的图片了！感谢分享！"""

# ------------------------ 天气功能相关消息 ------------------------ #
# 首次使用天气功能提示
WEATHER_FIRST_USE_PROMPT = """🌤️ 天气查询

您还没有设置常用城市~

请发送您的城市名称（如：北京、上海）
或发送您的位置，我将自动记录并查询天气。

发送「取消」退出设置"""

# 天气城市设置成功
WEATHER_CITY_SET_SUCCESS = """✅ 已记住您的城市：{city}

下次发送「天气」将直接查询该城市天气~
发送「更换城市」可以修改哦~"""

# 更换城市提示
WEATHER_CHANGE_CITY_PROMPT = """🏙️ 更换天气城市

当前城市：{current_city}

请发送新的城市名称或发送您的位置~

发送「取消」保持当前设置"""

# 取消城市设置
WEATHER_CITY_CANCELLED = """❌ 已取消

发送「天气」继续查询天气~"""

# 每日首次互动天气提醒（附加在正常回复后面）
DAILY_WEATHER_GREETING = """

---
🌤️ 今日天气 | {city}
🌡️ {temp}°C | {weather}
👔 {clothing_advice}"""

# ------------------------ 天气推送订阅相关消息 ------------------------ #
# VIP专属提示
WEATHER_PUSH_VIP_ONLY = """😢 天气推送是VIP专属功能哦~

发送「验证」进行身份验证，成为VIP后即可使用！"""

# 已订阅提示
WEATHER_PUSH_ALREADY_SUBSCRIBED = """📢 您已订阅天气推送

📍 推送城市：{city}

每日首次互动时将为您播报天气~

发送「取消订阅天气」可关闭推送"""

# 订阅前需先设置城市
WEATHER_PUSH_SUBSCRIBE_NO_CITY = """⚠️ 请先设置您的城市

发送「天气」设置常用城市后，再来订阅天气推送~"""

# 订阅成功
WEATHER_PUSH_SUBSCRIBE_SUCCESS = """✅ 天气推送订阅成功！

📍 推送城市：{city}

每日首次互动时将为您播报天气~

发送「取消订阅天气」可随时关闭"""

# 未订阅提示
WEATHER_PUSH_NOT_SUBSCRIBED = """您还没有订阅天气推送~

发送「订阅天气」开启每日天气提醒"""

# 取消订阅成功
WEATHER_PUSH_UNSUBSCRIBE_SUCCESS = """✅ 已取消天气推送

发送「订阅天气」可重新开启~"""

# 推送状态查询
WEATHER_PUSH_STATUS = """🌤️ 天气推送状态

📊 订阅状态：{status}
📍 推送城市：{city}

💡 {action_hint}"""

# ------------------------ 通知服务配置 ------------------------ #
# Server酱配置（推荐，免费且简单）
# 获取SendKey: https://sct.ftqq.com/
SERVER_CHAN_SEND_KEY = 'SCT306181TiZi7EPhAsxmbH0dQsDPQa76n'  # 请填入您的Server酱SendKey

# 邮件通知配置（可选）
SMTP_SERVER = ''  # SMTP服务器，如 smtp.qq.com
SMTP_PORT = 465  # SMTP端口，SSL一般为465
SMTP_USER = ''  # 发件人邮箱
SMTP_PASSWORD = ''  # 邮箱授权码（不是登录密码）
NOTIFY_EMAIL = ''  # 接收通知的邮箱

# ------------------------ 每日天气草稿配置 ------------------------ #
# 草稿创建时间（24小时制）
MASS_SEND_TIME = '07:00'

# 群发天气的城市
MASS_SEND_WEATHER_CITY = '广州'

# 封面图片的media_id（永久素材ID）
# 首次运行时会自动上传本地图片并打印media_id，请将其填入此处以避免重复上传
MASS_SEND_THUMB_MEDIA_ID = 'FYWfqM3tyUNscjY1NSDFR-MVb21TL650Sy4RYytJjppcMIvVKK1LTIXWIpIQdOkt'

# 封面图片本地路径（如果MASS_SEND_THUMB_MEDIA_ID为空，则使用此路径上传）
# 建议使用绝对路径，图片尺寸建议：900x383 或 2.35:1 比例
MASS_SEND_WEATHER_IMAGE_PATH = 'data/weather_cover.jpg'

# 图文消息标题模板（不能含特殊字符和emoji）
MASS_SEND_WEATHER_TITLE = '{date} {city}天气播报'

# 图文消息作者
MASS_SEND_AUTHOR = '源源和娇娇'

# 图文消息摘要
MASS_SEND_DIGEST = '今日天气早知道，出门穿衣有参考~'

# 图文消息HTML内容模板
MASS_SEND_WEATHER_HTML = """
<section style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 20px;">
    <h2 style="margin: 0 0 10px 0; font-size: 24px;">☀️ 早安！今天是{date} {weekday}</h2>
    <p style="margin: 0; font-size: 16px; opacity: 0.9;">📍 {city}天气播报</p>
</section>

<section style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
    <h3 style="color: #333; margin: 0 0 15px 0; border-left: 4px solid #667eea; padding-left: 10px;">🌡️ 实时天气</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;">当前温度</td>
            <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #333; font-weight: bold; text-align: right;">{temp}°C</td>
        </tr>
        <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;">体感温度</td>
            <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #333; font-weight: bold; text-align: right;">{feel_temp}°C</td>
        </tr>
        <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;">天气状况</td>
            <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #333; font-weight: bold; text-align: right;">{weather}</td>
        </tr>
        <tr>
            <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #666;">相对湿度</td>
            <td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #333; font-weight: bold; text-align: right;">{humidity}%</td>
        </tr>
        <tr>
            <td style="padding: 10px 0; color: #666;">风向风力</td>
            <td style="padding: 10px 0; color: #333; font-weight: bold; text-align: right;">{wind_dir} {wind_scale}级</td>
        </tr>
    </table>
</section>

<section style="background: #fff3cd; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107;">
    <h3 style="color: #856404; margin: 0 0 10px 0;">👔 今日穿衣建议</h3>
    <p style="color: #856404; margin: 0; line-height: 1.6;">{clothing_advice}</p>
</section>

<section style="text-align: center; padding: 20px; color: #999;">
    <p style="margin: 0;">💕 祝您今天心情愉快！</p>
    <p style="margin: 5px 0 0 0; font-size: 12px;">—— 源源和娇娇的家 ——</p>
</section>
"""

# ------------------------ 签到积分系统配置 ------------------------ #

# 签到积分规则
CHECKIN_BASE_POINTS = 10  # 基础签到积分
CHECKIN_STREAK_BONUS_3 = 20  # 连续3天额外奖励
CHECKIN_STREAK_BONUS_7 = 50  # 连续7天额外奖励
CHECKIN_VIP_MULTIPLIER = 2  # VIP积分倍数


# 签到成功消息模板
CHECKIN_SUCCESS = """✅ 签到成功！

📅 连续签到：{consecutive_days} 天
💰 获得积分：+{points_earned}{bonus_text}
💎 当前积分：{total_points}
🏆 累计签到：{total_checkins} 次

{vip_bonus_text}{streak_tip}
💡 坚持签到，积少成多~"""

# VIP积分翻倍提示
CHECKIN_VIP_BONUS_TEXT = '✨ VIP双倍积分已生效！\n'

# 连续签到奖励提示
CHECKIN_BONUS_TIP_3 = '\n🎁 再签{days}天可获得连续3天奖励+20积分！'
CHECKIN_BONUS_TIP_7 = '\n🎁 再签{days}天可获得连续7天奖励+50积分！'
CHECKIN_BONUS_GOT_3 = '\n🎉 连续3天奖励已到账！'
CHECKIN_BONUS_GOT_7 = '\n🎉 连续7天奖励已到账！'

# 今日已签到消息
CHECKIN_ALREADY = """⏰ 今日已签到

📅 连续签到：{consecutive_days} 天
💎 当前积分：{total_points}
🏆 累计签到：{total_checkins} 次

明天再来签到吧~"""

# 我的积分消息模板
MY_POINTS_INFO = """💎 我的积分

💰 当前积分：{total_points}
📅 连续签到：{consecutive_days} 天
🏆 累计签到：{total_checkins} 次
🥇 排行榜第 {rank} 名（共{total_users}人）

{vip_status}
💡 发送「签到」每日领取积分
💡 发送「积分排行」查看排行榜"""

# 积分排行榜模板
POINTS_RANKING = """🏆 积分排行榜

{ranking_list}

——————————
📊 您的排名：第 {my_rank} 名
💎 您的积分：{my_points}

💡 每日签到可获得积分哦~"""

# 排行榜行模板
RANKING_LINE = '{rank}. {name} - {points}分 ({checkins}次)'
RANKING_LINE_VIP = '{rank}. {name}👑 - {points}分 ({checkins}次)'

# 签到帮助消息
CHECKIN_HELP = """📝 签到积分说明

📌 每日签到可获得积分：
• 基础积分：10分
• 连续签到加成：每天+2分（最高+20分）
• 连续3天奖励：额外+20分
• 连续7天奖励：额外+50分

✨ VIP专属福利：
• 所有积分翻倍！

🎯 积分用途：
• 即将开放积分兑换功能~

💡 发送「签到」开始领取积分吧！"""

# 非VIP积分状态提示
POINTS_NOT_VIP = '💡 发送「验证」成为VIP，签到积分翻倍！'
POINTS_IS_VIP = '👑 您是尊贵的VIP，签到积分双倍！'

# ------------------------ 昵称功能相关消息 ------------------------ #
# 昵称长度限制
NICKNAME_MIN_LENGTH = 2
NICKNAME_MAX_LENGTH = 12

# 设置昵称提示
NICKNAME_SET_PROMPT = """✏️ 设置昵称

当前昵称：{current_nickname}

请发送您想要的昵称（{min_len}-{max_len}个字符）

💡 昵称将在签到、排行榜等功能中显示

发送「取消」退出设置"""

# 昵称设置成功
NICKNAME_SET_SUCCESS = """✅ 昵称设置成功！

您的昵称已更新为：{nickname}

💡 发送「设置昵称」可随时修改"""

# 昵称无效
NICKNAME_INVALID = """❌ 昵称格式无效

昵称要求：
• 长度 {min_len}-{max_len} 个字符
• 不能包含特殊符号

请重新输入昵称，或发送「取消」退出"""

# 取消设置昵称
NICKNAME_SET_CANCELLED = """❌ 已取消设置昵称

发送「设置昵称」可重新设置"""

# 查看昵称
NICKNAME_INFO = """📛 我的昵称

当前昵称：{nickname}

💡 发送「设置昵称」可修改昵称"""

# 默认昵称前缀（用于未设置昵称的用户）
NICKNAME_DEFAULT_PREFIX = '用户'
