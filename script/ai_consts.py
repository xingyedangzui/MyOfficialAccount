# -*- coding: utf-8 -*-
"""
AI 服务配置常量

集中管理所有 AI 服务的配置，方便维护和修改
"""

# ==================== 通义千问配置 ==================== #
# 阿里云百炼平台，每月免费额度
# 申请地址: https://bailian.console.aliyun.com/
# 模型列表: https://help.aliyun.com/zh/model-studio/getting-started/models
QWEN_API_KEY = 'sk-23f55cb1d83248149292506925b0916f'
QWEN_API_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
QWEN_MODEL = 'qwen-plus'  # 可选: qwen-turbo, qwen-plus, qwen-max


# ==================== 智谱 ChatGLM 配置 ==================== #
# 新用户赠送500万Token
# 申请地址: https://open.bigmodel.cn/
ZHIPU_API_KEY = '3261c9ce585444aea9dda0f2e24caecb.ZudI1qxPltRY3lwJ'
ZHIPU_API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
ZHIPU_MODEL = 'glm-4-flash'  # 免费模型

# 智谱 AI 官方 SDK 检测
try:
    from zai import ZhipuAiClient

    ZHIPU_SDK_AVAILABLE = True
except ImportError:
    ZHIPU_SDK_AVAILABLE = False
    print('[AI] 智谱 SDK (zai) 未安装，将使用 HTTP 方式调用')


# ==================== SiliconFlow 硅基流动配置 ==================== #
# 每日免费额度，支持多种开源模型
# 申请地址: https://cloud.siliconflow.cn/
# 免费模型: Qwen/Qwen2.5-7B-Instruct, tencent/Hunyuan-MT-7B 等
SILICONFLOW_API_KEY = 'sk-ngocymqxsyrlemauoszhywrzetlyetucismneddfrwmwhaft'
SILICONFLOW_API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
SILICONFLOW_MODEL = 'tencent/Hunyuan-MT-7B'  # 翻译模型


# ==================== 讯飞星火配置 ==================== #
# Spark X1.5 - 300万Token额度
# 申请地址: https://xinghuo.xfyun.cn/
# 官方文档: https://www.xfyun.cn/doc/spark/HTTP调用文档.html
SPARK_APPID = 'afcbb872'
SPARK_API_KEY = '54b74d8c45a30f8eb4787cc1a3feb608'
SPARK_API_SECRET = 'MWRjMjQzMmFlZjVkNGIxYzhiNzhjZDBh'
SPARK_API_URL = 'https://spark-api-open.xf-yun.com/v2/chat/completions'
SPARK_MODEL = 'spark-x'  # Spark X1.5 深度推理模型


# ==================== AI 服务优先级配置 ==================== #
# 默认优先级：用于普通聊天/问答
AI_SERVICE_PRIORITY = ['zhipu', 'qwen', 'spark']

# 翻译专用优先级：优先使用翻译模型
AI_SERVICE_PRIORITY_TRANSLATE = ['siliconflow', 'zhipu', 'qwen', 'spark']


# ==================== 请求配置 ==================== #
# 请求超时时间（秒）
# 注意：微信公众号被动回复要求5秒内响应，超时会导致用户收不到回复
# 可以考虑使用异步客服消息方式来解决超时问题
AI_REQUEST_TIMEOUT = 10  # 本地测试可以用较长时间

# 模型参数
AI_MAX_TOKENS = 300  # 最大生成Token数
AI_TEMPERATURE = 0.7  # 温度参数 (0-1，越高越随机)


# ==================== 对话历史配置 ==================== #
MAX_HISTORY_LENGTH = 10  # 保留的最大历史对话轮数
CONVERSATION_EXPIRE_SECONDS = 3600  # 对话过期时间（秒）


# ==================== 系统提示词 ==================== #
AI_SYSTEM_PROMPT = """你是「源源和娇娇的家」微信公众号的智能助手，名叫"小源"。

你的特点：
- 性格温暖、活泼、有趣
- 回复简洁但不失温度，每次回复控制在150字以内
- 喜欢使用适当的emoji表情
- 会根据用户的问题提供帮助
- 如果遇到不知道的问题，会坦诚地说不知道

你可以帮助用户：
- 闲聊解闷
- 回答各种问题
- 提供生活建议
- 讲笑话、说故事

请用自然、亲切的语气回复用户。"""

AI_SYSTEM_PROMPT_TRANSLATE = """你是一个专业的翻译助手。

任务要求：
1. 准确翻译用户提供的内容
2. 如果是中文，翻译成英文；如果是外文，翻译成中文
3. 保持原文的语气和风格
4. 只输出翻译结果，不要额外解释
5. 如果用户指定了目标语言，按照用户要求翻译

请直接输出翻译结果。"""


# ==================== 意图识别配置 ==================== #
# 翻译相关关键词
TRANSLATE_KEYWORDS = [
    # 明确的翻译指令
    '翻译',
    '译成',
    '译为',
    '译一下',
    '帮我翻',
    '翻成',
    '翻为',
    'translate',
    'translation',
    # 语言转换表达
    '中译英',
    '英译中',
    '中翻英',
    '英翻中',
    '日译中',
    '中译日',
    '韩译中',
    '中译韩',
    '法译中',
    '中译法',
    '德译中',
    '中译德',
    # 常见翻译请求模式
    '用英语怎么说',
    '用中文怎么说',
    '用日语怎么说',
    '英语怎么说',
    '中文怎么说',
    '日语怎么说',
    '什么意思',  # "这句话什么意思" 常用于求翻译
    # 语言名称 + 动词
    '翻译成中文',
    '翻译成英文',
    '翻译成英语',
    '翻译成日语',
]

# 翻译请求的正则模式
TRANSLATE_PATTERNS = [
    r'把.+翻译成',  # 把xxx翻译成英文
    r'将.+翻译成',  # 将xxx翻译成中文
    r'.+怎么翻译',  # xxx怎么翻译
    r'翻译[：:].+',  # 翻译：xxx 或 翻译:xxx
    r'[a-zA-Z]{3,}',  # 包含较长英文单词（可能是求翻译）
]


# ==================== 备用回复配置 ==================== #
FALLBACK_REPLIES = {
    'greeting': '你好呀！😊 很高兴见到你~',
    'thanks': '不客气！有什么需要随时问我哦~ 😄',
    'goodbye': '再见啦！下次再聊~ 👋',
    'joke': '为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 = Dec 25 🤣',
    'question': '这个问题很有趣！不过我现在有点忙，晚点再详细回答你哦~ 😅',
    'default': '收到你的消息啦！我现在有点忙，待会儿再跟你好好聊~ 😊',
}
