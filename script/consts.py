# ------------------------ 字符串常量区------------------------- #
HOST = '0.0.0.0:80'  # 生产环境监听所有IP地址的80端口
TOKEN = 'xiexingyuan'  # 微信公众平台配置的Token

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


# ------------------------ 菜谱功能相关消息 ------------------------ #
# 一级帮助菜单
HELP_MESSAGE = """📖 功能列表

1️⃣ 发送「菜谱」- 菜谱相关功能
2️⃣ 发送「验证」- 身份验证成为VIP
3️⃣ 发送「我的VIP」- 查看VIP信息

💡 直接发送对应文字即可~"""

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

# 菜谱列表模板
RECIPE_LIST_TEMPLATE = """📖 菜谱列表

{recipe_list}

共 {total} 个菜谱
发送「菜谱 序号」查看详情"""

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
